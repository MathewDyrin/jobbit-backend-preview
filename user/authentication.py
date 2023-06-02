import hashlib
from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class JWTAuthentication(BaseJWTAuthentication):
    def authenticate(self, request):
        # refactor this
        data = super().authenticate(request)
        if not data:
            return data
        user, validated_token = data
        session_key = hashlib.sha256(str.encode(str(validated_token) + str(user.id))).hexdigest()
        if not user.session_set.filter(key=session_key):
            raise InvalidToken
        return user, validated_token


class PhoneOrEmailBackend(ModelBackend):
    def authenticate(self, request, **credentials):
        phone_number = credentials.get('phone_number')
        email = credentials.get('email')
        password = credentials.get('password')
        username = None
        username_key = None

        if email and phone_number:
            return

        if email:
            username = email
            username_key = 'email'

        if phone_number:
            username = phone_number
            username_key = 'phone_number'

        if username is None or password is None:
            return

        try:
            user = UserModel._default_manager.get_by_natural_key({'key': username_key, 'value': username})
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
