from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainSerializer as BaseTokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.validators import validate_international_phonenumber
from drf_extra_fields.fields import Base64ImageField as DefaultBase64ImageField
from .otp import OTP, OTPException
from . import auth
from .models import UserSettingsMixin


User = get_user_model()


class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})
        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True
        super().__init__(*args, **kwargs)


class Base64ImageField(DefaultBase64ImageField):
    ALLOWED_TYPES = getattr(settings, 'SUPPORTED_IMAGE_TYPES')


class GuestSerializer:
    pass


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone_number', 'is_2FA_enabled', 'type_2FA',)
        read_only_fields = ('email', 'phone_number', 'is_2FA_enabled', 'type_2FA',)


class UserPhoneCreateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[validate_international_phonenumber])
    password = serializers.CharField()
    re_password = serializers.CharField()

    default_error_messages = {
        'phone_number_is_busy': 'User with given phone number already exists',
    }

    class Meta:
        model = User
        fields = ('phone_number', 'password', 're_password',)
        read_only_fields = ('re_password',)

    def validate(self, attrs):
        data = super().validate(attrs)
        if User.objects.filter(phone_number=data['phone_number']):
            self.fail('phone_number_is_busy')
        data['password'] = make_password(data['password'])
        data['re_password'] = make_password(data['re_password'])
        data['is_active'] = False
        data['type_2FA'] = UserSettingsMixin.Type2FA.PHONE
        return data


class UserDeleteSerializer(serializers.Serializer):
    default_error_messages = {
        'no_active_account': 'No active account found with the given credentials',
    }
    password = PasswordField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        self.user = self.context['request'].user
        if self.user and self.user.check_password(attrs.get('password')):
            return {'user_id': str(self.user.id)}
        raise self.fail('no_active_account')


class UserPasswordRecoverSerializer(serializers.Serializer):
    default_error_messages = {
        'no_fields_provided': 'Need to provide email or phone number',
        'no_active_account': 'No active account found with the given credentials'
    }
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False, validators=[validate_international_phonenumber])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate_email(self, email):
        if not auth.get_user({'email': email}):
            return None
        return email

    def validate_phone_number(self, phone_number):
        if not auth.get_user({'phone_number': phone_number}):
            return None
        return phone_number

    def validate(self, attrs):
        if len(attrs) == 0:
            self.fail('no_fields_provided')

        if attrs.get('email'):
            self.user = auth.get_user({'email': attrs.get('email')})
            return True

        if attrs.get('phone_number'):
            self.user = auth.get_user({'phone_number': attrs.get('phone_number')})
            return True

        self.fail('no_active_account')


class CodeAndTokenSerializer(serializers.Serializer):
    default_error_messages = {
        'invalid_token_or_code': 'Invalid token or code for given user',
    }
    token = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        try:
            payload = OTP.verify(token=attrs.get('token'), code=attrs.get('code'))
            user_id = payload.get('user_id')
            if user_id:
                self.user = auth.get_user({'id': user_id})
                if self.user:
                    return payload
        except OTPException:
            pass
        self.fail('invalid_token_or_code')


class PhoneNumberChangeSerializer(serializers.Serializer):
    default_error_messages = {
        'phone_number_is_busy': 'User with given phone number already exists',
    }
    phone_number = PhoneNumberField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate_phone_number(self, phone_number):
        if auth.get_user({'phone_number': phone_number}):
            self.fail('phone_number_is_busy')
        return phone_number

    def validate(self, attrs):
        self.user = self.context['request'].user
        return {
            'user_id': str(self.user.id),
            'phone_number': str(attrs.get('phone_number')),
        }


class EmailResetSerializer(serializers.Serializer):
    default_error_messages = {
        'email_is_busy': 'User with given email address already exists'
    }
    email = serializers.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate_email(self, email):
        user = auth.get_user({'email': email}, only_active_users=False)
        if user:
            self.fail('email_is_busy')
        return email


class TokenFunctionsMixin:
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)


class TokenObtainPairSerializer(TokenFunctionsMixin, BaseTokenObtainSerializer):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if request.data.get('phone_number'):
            self.username_field = 'phone_number'
            self.fields.pop('email')
            self.fields['phone_number'] = serializers.CharField(validators=[validate_international_phonenumber])

        else:
            self.username_field = 'email'
            self.fields['email'] = serializers.CharField(validators=[validate_email])

    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.is_2FA_enabled and self.user.phone_number:
            return {'user_id': str(self.user.id), 'phone_number': str(self.user.phone_number)}
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data


class TokenObtainPairCodeAndTokenSerializer(TokenFunctionsMixin, CodeAndTokenSerializer):

    def validate(self, attrs):
        super().validate(attrs)
        refresh = self.get_token(self.user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class TokenReviewSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class Select2FAMethodSerialzier(serializers.Serializer):
    method = serializers.ChoiceField(choices=UserSettingsMixin.Type2FA.choices)


# TODO: Use as basement to implement client profile and executor avatar setting
# class ImageValidatorMixin:
#     default_error_messages = {
#         'large_image': 'Image size is too large',
#     }
#
#     def validate_image(self, image):
#         if image.size > getattr(settings, 'MAX_IMAGE_SIZE'):
#             self.fail('large_image')
#         return image


# TODO: Use as basement to implement client profile and executor profile verification
# class UserVerificationSerializer(serializers.ModelSerializer):
#     full_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Verification
#         fields = '__all__'
#
#     def get_full_name(self, obj):
#         return obj.get_full_name()
