"""
Django settings for jobbit project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path
import environs

env = environs.Env()
environs.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-m)-c3#90r$9#1vkkdmi4nx$iadxcq*3owrs)#p#i47ajs#r+g-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # INNER APPS
    'user.apps.UserConfig',
    'geo.apps.GeoConfig',
    'notification.apps.NotificationConfig',
    'cli.apps.CliConfig',
    'category.apps.CategoryConfig',
    'client.apps.ClientConfig',
    'executor.apps.ExecutorConfig',
    'order.apps.OrderConfig',
    'chat.apps.ChatConfig',
    'transactions.apps.TransactionsConfig',

    # THIRD PARTY LIBS
    'rest_framework',
    'djoser',
    'rest_framework_simplejwt',
    'corsheaders',
    'anymail',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jobbit.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jobbit.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASE_ROUTERS = ['jobbit.routers.OrderRouter']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env('DB_NAME'),
        "USER": env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT')
    },
    # "order": {
    #     "ENGINE": "djongo",
    #     "NAME": "jobbit"
    # }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    'user.authentication.PhoneOrEmailBackend',
    'django.contrib.auth.backends.ModelBackend'
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/api/static/'
STATIC_ROOT = '/home/jobbit-backend/static/'

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Extend django anonymous user model

AUTH_ANONYMOUS_MODEL = 'user.models.Guest'

# For accessing django admin site

AUTH_USER_MODEL = 'user.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'user.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 35,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ]
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

DOMAIN = env("FRONTEND_URL")
SITE_NAME = ("Jobbit")
DJOSER = {
    'SERIALIZERS': {
        'user_create': 'user.serializers.UserCreateSerializer'
    },
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SET_USERNAME_RETYPE': True,
    'SET_PASSWORD_RETYPE': True,
    'SEND_ACTIVATION_EMAIL': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'email/reset/confirm/{uid}/{token}?new_email={new_email}',
    'EMAIL': {
        'activation': 'user.email.ActivationEmail',
        'password_reset': 'user.email.PasswordResetEmail',
    },
}

# OAuth2
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URL = env("GOOGLE_REDIRECT_URL")

VK_CLIENT_ID = env("VK_CLIENT_ID")
VK_CLIENT_SECRET = env("VK_CLIENT_SECRET")
VK_REDIRECT_URL = env("VK_REDIRECT_URL")

YANDEX_CLIENT_ID = env("YANDEX_CLIENT_ID")
YANDEX_CLIENT_SECRET = env("YANDEX_CLIENT_SECRET")
YANDEX_REDIRECT_URL = env("YANDEX_REDIRECT_URL")

FRONTEND_URL = env("FRONTEND_URL")
FRONTEND_PROTOCOL = env("FRONTEND_PROTOCOL")

# For sending mails
ANYMAIL = {
    "MAILGUN_API_KEY": env("MAILGUN_API_KEY"),
    "MAILGUN_API_URL": env("MAILGUN_API_URL"),
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = env("SERVER_EMAIL")


CORS_ALLOWED_ORIGINS = [
    'http://localhost:3030',
    'http://localhost:3000',
    'http://localhost:4000',
    'http://localhost:5173',
]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000'
]
CORS_ORIGIN_ALLOW_ALL = True  # If this is used then `CORS_ORIGIN_WHITELIST` will not have any effect
CORS_ALLOW_CREDENTIALS = True

SUPPORTED_IMAGE_TYPES = ('jpeg', 'jpg', 'png',)
MAX_IMAGE_SIZE = 8388608
SEND_USER_ACCOUNT_DELETE_CONFIRMATION_EMAIL = True
VERIFICATION_CODE_LENGTH = 6
SMS_AERO_SIGNATURE = 'Sms Aero'
SMS_AERO_API_KEY = 'dq8VmgEJejTjjyOBaYVZ9ZCWZUj'
SMS_AERO_EMAIL = 'example@mail.com'
SMS_VERIFICATION_TEXT = 'VERIFICATION CODE: {}'
SMS_MESSAGE = {
    'DEFAULT_SMSER': 'TelegramSmsMessage'
}

# LOGGING = {
#     'version': 1,
#     'handlers': {
#         'console': {'class': 'logging.StreamHandler'}
#     },
#     'loggers': {
#         'django.db.backends': {
#             'handlers': ['console'],
#             'level': 'DEBUG'
#         }
#     }
# }

# Storage settings
STORAGE = {
    'DEFAULT_STORAGE': 'S3ObjectStorage',
    'ALLOWED_TYPES': (
        'image/png', 'image/jpeg',
        'image/webp', 'application/pdf',
        'application/csv', 'application/docx',
    ),
    'MAX_SIZES': {
        'image/png': 10485760,
        'image/jpeg': 10485760,
        'image/webp': 10485760,
    }
}

#  S3 settings
S3_ACCESS_KEY_ID = env('S3_ACCESS_KEY_ID')
S3_ACCESS_SECRET_KEY = env('S3_ACCESS_SECRET_KEY')
S3_BUCKET_NAME = env('S3_BUCKET_NAME')
S3_ENDPOINT_URL = env('S3_ENDPOINT_URL')
S3_ACCESS_URL = env('S3_ACCESS_URL')

#  Telegram BOT
TG_BOT_TOKEN = env('TG_BOT_TOKEN')
TG_CHAT_ID = env('TG_CHAT_ID')

# Stripe settings
STRIPE_API_KEY = env("STRIPE_API_KEY")

# CryptoCloudPayments settings
CCP_API_KEY = env("CCP_API_KEY")
CCP_SHOP_ID = env("CCP_SHOP_ID")
