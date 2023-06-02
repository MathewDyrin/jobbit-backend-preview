import jwt
import datetime
import random
import string
from django.conf import settings


class OTPException(Exception):
    pass


class OTP:
    __internal_storage = {}

    @classmethod
    def generate(cls, *, payload: dict, expiration: int = 5, pattern: str = 'num') -> tuple:
        """
        :param payload: data stored in token
        :param expiration: how long validation code alive, type - datetime.timedelta
        :param pattern: what characters use at code, num - numbers, let - letters, type - string
        :return: token, code
        """
        payload.update({'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration)})
        token = jwt.encode(payload=payload, key=getattr(settings, 'SECRET_KEY', ''))
        sample = string.ascii_uppercase if pattern == 'let' else list(map(str, range(10)))
        code = ''.join(random.sample(sample, getattr(settings, 'VERIFICATION_CODE_LENGTH')))
        cls.__internal_storage[token] = code
        return token, code

    @classmethod
    def verify(cls, *, token: str, code: str) -> dict:
        """
        :param token: encoded jwt token
        :param code: validation code
        :return: payload
        """
        if token and code == cls.__internal_storage.get(token):
            del cls.__internal_storage[token]
            try:
                return jwt.decode(jwt=token, key=getattr(settings, 'SECRET_KEY', ''), algorithms=['HS256'])
            except (jwt.exceptions.DecodeError, jwt.ExpiredSignatureError,):
                pass
        raise OTPException('Incorrect token or code')
