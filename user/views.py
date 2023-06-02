import uuid
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser import signals
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions as rest_framework_permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.conf import settings as djoser_settings
from djoser.compat import get_user_email
from djoser import serializers as djoser_serializers
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView
from rest_framework_simplejwt import exceptions
from django.http import HttpResponseRedirect
from . import email as email_message
from . import otp
from . import sms
from . import permissions
from . import serializers
from . import auth
from . import adapters
from . import models

User = get_user_model()


class DjoserUserOverride(DjoserUserViewSet):
    permission_classes_by_action = {
        'reset_password': [rest_framework_permissions.AllowAny]
    }

    def get_permissions(self):
        if not self.permission_classes_by_action.get(self.action):
            return []
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    def _perform_create(self, serializer):
        user = serializer.save()
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )
        context = {"user": user}
        activation = email_message.ActivationEmail(context=context)
        activation = activation.get_context_data()
        activation_url = f"{activation['protocol']}://" \
                         f"{activation['domain']}/" \
                         f"{activation['uid']}/" \
                         f"{activation['token']}"
        sms.Smser().send([user.phone_number], text=activation_url)
        return user

    def create(self, request, *args, **kwargs):
        if request.data.get('phone_number'):
            serializer = serializers.UserPhoneCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data.pop('re_password')
            user = self._perform_create(serializer)
            serializer.validated_data.pop('is_active')
            serializer.validated_data.pop('password')
            serializer.validated_data['id'] = user.pk
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        else:
            data = super().create(request, *args, **kwargs)
            return data

    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            serializer = serializers.UserPasswordRecoverSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
        else:
            user = request.user

        if user.type_2FA == models.UserSettingsMixin.Type2FA.EMAIL:
            request.data['email'] = user.email
            return super().reset_password(request, *args, **kwargs)
        else:
            context = {"user": user}
            reset = email_message.ActivationEmail(context=context)
            reset = reset.get_context_data()
            reset_url = f"{reset['protocol']}://" \
                        f"{reset['domain']}/password/reset/confirm/" \
                        f"{reset['uid']}/" \
                        f"{reset['token']}"
            sms.Smser().send([user.phone_number], text=reset_url)
            return Response(status=status.HTTP_204_NO_CONTENT)


class SendVerificationSmsMixin:

    def send(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # generate jwt token here to send via sms
        print(serializer.validated_data)
        token, code = otp.OTP.generate(payload=serializer.validated_data)
        print(serializer.validated_data.get('phone_number'))
        self.perform_send_sms(
            phone_number=serializer.validated_data.get('phone_number'),
            code=code
        )
        return Response(
            data={'token': token},
            status=status.HTTP_200_OK
        )

    @staticmethod
    def perform_send_sms(phone_number, code):
        # send may occur SmsException
        text = getattr(settings, 'SMS_VERIFICATION_TEXT', '').format(code)
        print(text)
        print(sms.Smser().send(
            number_list=[str(phone_number)],
            text=text)
        )


# provides get_authenticate_header and permission classes
class GenericTokenObtainPairViewSet(viewsets.ViewSetMixin, TokenViewBase):
    pass


class TokenObtainPairViewSet(SendVerificationSmsMixin, GenericTokenObtainPairViewSet):
    serializer_class = serializers.TokenObtainPairSerializer

    def get_serializer_class(self):
        if self.action == 'confirm':
            return serializers.TokenObtainPairCodeAndTokenSerializer
        return serializers.TokenObtainPairSerializer

    @action(detail=False, methods=['POST'])
    def generate(self, request, *args, **kwargs):
        serializer = self.get_serializer(request=request, data=request.data)
        # idk why it may occur token error
        try:
            serializer.is_valid(raise_exception=True)
        except exceptions.TokenError as e:
            raise exceptions.InvalidToken(e.args[0])
        access = serializer.validated_data.get('access')
        refresh = serializer.validated_data.get('refresh')
        user = serializer.user

        if access and refresh:
            auth.login_user(user=user, access=access, refresh=refresh, request=request)
            return Response(
                data=serializer.validated_data,
                status=status.HTTP_200_OK
            )

        token, code = otp.OTP.generate(payload=serializer.validated_data)

        if user.type_2FA == models.UserSettingsMixin.Type2FA.PHONE:
            SendVerificationSmsMixin.perform_send_sms(user.phone_number, code)
        else:
            context = {'code': code}
            to = [get_user_email(user)]
            # move email class to settings
            # TODO: move another template
            email_message.UserAccountDeleteEmail(self.request, context).send(to)

        return Response(
            data={'token': token},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['POST'])
    def confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access = serializer.validated_data.get('access')
        refresh = serializer.validated_data.get('refresh')
        auth.login_user(user=serializer.user, access=access, refresh=refresh, request=request)
        return Response(
            data=serializer.validated_data,
            status=status.HTTP_200_OK
        )


class TokenRefreshView(BaseTokenRefreshView):

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        access = response.data.get('access')
        refresh = request.data.get('refresh')
        user_id = auth.get_user_id(token=access)
        user = User.objects.filter(id=user_id).first()
        if user:
            result = auth.refresh_session(refresh=refresh, access=access)
            if result:
                response.data['refresh'] = refresh
                return response
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class TokenDestroyView(APIView):

    def post(self, request, *args, **kwargs):
        access = request.headers.get('Authorization').split(' ')[1]
        auth.logout_user(request.user, access)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  SendVerificationSmsMixin,
                  viewsets.GenericViewSet):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.filter(is_active=True,
                                   is_superuser=False,
                                   is_staff_member=False)
    # forgot what it is for, need to check
    token_generator = default_token_generator

    # move permission classes to settings
    def get_permissions(self):
        if self.action == 'destroy':
            self.permission_classes = [permissions.StaffMemberOrSuperuser, ]
        elif self.action in ['update', 'partial_update', ]:
            self.permission_classes = [permissions.CurrentUser, ]
        elif self.action in ['me', 'confirm_reset_password', ]:
            self.permission_classes = [rest_framework_permissions.AllowAny, ]
        return super().get_permissions()

    # move serializer classes to settings
    def get_serializer_class(self):
        if self.action == 'me':
            return serializers.TokenReviewSerializer
        elif self.action == 'reset_email':
            return serializers.EmailResetSerializer
        elif self.action == 'change_phone_number':
            return serializers.PhoneNumberChangeSerializer
        elif self.action == 'delete_user_account':
            return serializers.UserDeleteSerializer
        elif self.action == 'confirm_reset_password':
            return djoser_serializers.PasswordResetConfirmSerializer
        elif self.action in [
            'confirm_delete_user_account',
            'confirm_change_phone',
            'confirm_switch_2fa',
            'confirm_select_2fa_method',
        ]:
            return serializers.CodeAndTokenSerializer
        elif self.action == 'select_2fa_method':
            return serializers.Select2FAMethodSerialzier
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        # media will only be deleted through the serializer
        # to delete not through the serializer, this must be implemented as a signal
        for media in [instance.header_avatar]:
            if media:
                # TODO: implement method that delete avatars from s3 storage
                media.delete()
        super().perform_destroy(instance)

    @action(detail=False, methods=['POST'])
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO: remove token
        token = serializer.validated_data.get('token')
        user_id = auth.get_user_id(token)
        if user_id:
            return Response(
                data={'user_id': user_id},
                status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def profile(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        return Response(data=serializer.data)

    @action(detail=False, methods=['POST'])
    def change_phone_number(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # generate jwt token to send via email
        phone_number = serializer.validated_data['phone_number']
        token, code = otp.OTP.generate(payload=serializer.validated_data)
        SendVerificationSmsMixin.perform_send_sms(phone_number, code)
        return Response(
            data={'token': token},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['POST'])
    def confirm_change_phone(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        payload = serializer.validated_data
        user.phone_number = payload['phone_number']
        user.save()
        return Response({'phone_number': str(user.phone_number)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def reset_email(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        context = {'user': serializer.user, 'new_email': email}
        to = [email]
        # move email reset email to settings
        email_message.EmailResetEmail(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])
    def confirm_reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.set_password(serializer.data['new_password'])
        auth.logout_user(user, flush_all=True)
        if hasattr(user, 'last_login'):
            user.last_login = now()
        user.save()
        if djoser_settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {'user': user}
            to = [get_user_email(user)]
            djoser_settings.EMAIL.password_changed_confirmation(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])
    def delete_user_account(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_user_account_delete_confirmation_email = getattr(
            settings,
            'SEND_USER_ACCOUNT_DELETE_CONFIRMATION_EMAIL',
            False
        )
        user = serializer.user
        if send_user_account_delete_confirmation_email:
            # generate jwt token here to send via email or phone number
            token, code = otp.OTP.generate(payload=serializer.validated_data)

            if user.type_2FA == models.UserSettingsMixin.Type2FA.EMAIL:
                context = {'code': code}
                to = [get_user_email(user)]
                # move email class to settings
                email_message.UserAccountDeleteEmail(self.request, context).send(to)

            else:
                SendVerificationSmsMixin.perform_send_sms(user.phone_number, code)

            return Response(
                data={'token': token},
                status=status.HTTP_200_OK
            )
        self.perform_destroy(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])
    def confirm_delete_user_account(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_destroy(serializer.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])
    def switch_2fa(self, request, *args, **kwargs):
        # generate jwt token here to send via email
        user = request.user
        token, code = otp.OTP.generate(payload={'user_id': str(user.id)})

        if request.user.type_2FA == models.UserSettingsMixin.Type2FA.EMAIL:
            context = {'code': code}
            to = [get_user_email(user)]
            # move email class to settings
            # TODO: move another template
            email_message.UserAccountDeleteEmail(self.request, context).send(to)
        else:
            SendVerificationSmsMixin.perform_send_sms(user.phone_number, code)
        return Response(
            data={'token': token},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['POST'])
    def confirm_switch_2fa(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_2FA_enabled = not user.is_2FA_enabled
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])
    def select_2fa_method(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        method = serializer.validated_data['method']
        user = request.user

        token, code = otp.OTP.generate(
            payload={'user_id': str(user.id), 'type': method}
        )

        if method == models.UserSettingsMixin.Type2FA.PHONE:
            if user.phone_number:
                SendVerificationSmsMixin.perform_send_sms(user.phone_number, code)
                return Response(
                    data={'token': token},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'detail': 'User has not phone number'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if method == models.UserSettingsMixin.Type2FA.EMAIL:
            if user.email:
                context = {'code': code}
                to = [get_user_email(user)]
                # TODO: move another template
                email_message.UserAccountDeleteEmail(self.request, context).send(to)
                return Response(
                    data={'token': token},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'detail': 'User has not email'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(detail=False, methods=['POST'])
    def confirm_select_2fa_method(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        payload = serializer.validated_data
        user.type_2FA = payload['type']
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserOAuth2Providers(viewsets.GenericViewSet):
    vk_auth = adapters.VKAuth(
        settings.VK_CLIENT_ID,
        settings.VK_CLIENT_SECRET,
        settings.VK_REDIRECT_URL
    )

    google_auth = adapters.GoogleAuth(
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
        settings.GOOGLE_REDIRECT_URL
    )

    yandex_auth = adapters.YandexAuth(
        settings.YANDEX_CLIENT_ID,
        settings.YANDEX_CLIENT_SECRET,
        settings.YANDEX_REDIRECT_URL
    )

    permission_classes_by_action = {
        'auth': [rest_framework_permissions.AllowAny],
        'vk': [rest_framework_permissions.AllowAny],
        'google': [rest_framework_permissions.AllowAny],
        'yandex': [rest_framework_permissions.AllowAny],
        'generate': [rest_framework_permissions.AllowAny]
    }

    @staticmethod
    def validate_user(request, scope, scope_type='email'):
        if scope_type == 'phone_number':
            user = User.objects.filter(phone_number=scope).first()
        else:
            user = User.objects.filter(email=scope).first()

        if not user:
            user_data = {
                'password': make_password(uuid.uuid4().hex[::11]),
                'username': models.UserManager.generate_username(),
                scope_type: scope
            }
            user = User.objects.create(**user_data)
            user.save()

        tokens = serializers.TokenFunctionsMixin.get_token(user)
        access = str(tokens.access_token)
        refresh = str(tokens)

        auth.login_user(user=user, access=access, refresh=refresh, request=request)
        redirect_url = settings.FRONTEND_PROTOCOL + "://" + settings.FRONTEND_URL + \
                       f'/auth/provider?refresh={refresh}&access={access}'
        return HttpResponseRedirect(redirect_url)

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=['GET'])
    def auth(self, request, *args, **kwargs):
        method = request.GET.get('method')
        if not method:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if method == 'vk':
            login_url = self.vk_auth.login()
        elif method == 'google':
            login_url = self.google_auth.login()
        elif method == 'yandex':
            login_url = self.yandex_auth.login()
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return HttpResponseRedirect(login_url)

    @action(detail=False, methods=['GET'])
    def vk(self, request, *args, **kwargs):
        provider_data = self.vk_auth.get_tokens(request.GET['code'])
        email = provider_data.get('email')
        if not email:
            email = f"{provider_data['user_id']}.oauth2vk@omw.com"
        return self.validate_user(request, email)

    @action(detail=False, methods=['GET'])
    def google(self, request, *args, **kwargs):
        tokens = self.google_auth.get_tokens(request.GET['code'])
        provider_data = self.google_auth.get_user_data_from_token(tokens['access_token'])
        email = provider_data['email']
        return self.validate_user(request, email)

    @action(detail=False, methods=['GET'])
    def yandex(self, request, *args, **kwargs):
        tokens = self.yandex_auth.get_tokens(request.GET['code'])
        provider_data = self.yandex_auth.get_user_data_from_token(tokens['access_token'])
        email = provider_data['default_email']
        return self.validate_user(request, email)


# TODO: Use as basement to implement client profile and executor profile verification
# class UserVerificationView(APIView):
#     permission_classes = [rest_framework_permissions.IsAuthenticated]
#
#     def post(self, request) -> Response:
#         request.data['user'] = request.user.id
#         serializer = serializers.UserVerificationSerializer(data=request.data)
#
#         if serializer.is_valid():
#             new_verification = serializer.create(serializer.validated_data)
#             return Response(
#                 serializers.UserVerificationSerializer(new_verification).data,
#                 status=status.HTTP_201_CREATED
#             )
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
