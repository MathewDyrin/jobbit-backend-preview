import jwt
import hashlib
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Session
from common_helpers import http_request
User = get_user_model()


def get_user(data, only_active_users=True):
    if only_active_users:
        data['is_active'] = True
    try:
        user = User.objects.get(**data)
        if user.has_usable_password():
            return user
    except User.DoesNotExist:
        pass


def get_user_id(token):
    try:
        validated_token = jwt.decode(token, getattr(settings, 'SECRET_KEY', ''), algorithms=["HS256"])
    except (jwt.exceptions.DecodeError, jwt.ExpiredSignatureError, ):
        return None
    return validated_token['user_id']


def logout_user(user, access=None, flush_all=False):
    if flush_all:
        sessions = Session.objects.filter(user=user).all()
        for session in sessions:
            session.delete()
    else:
        try:
            session_key = hashlib.sha256(str.encode(str(access) + str(user.id))).hexdigest()
            session = Session.objects.get(key=session_key)
            session.delete()
        except Session.DoesNotExist:
            pass


def refresh_session(refresh, access):
    session = Session.objects.filter(refresh_token=refresh).first()
    if session:
        session_key = hashlib.sha256(str.encode(str(access) + str(session.user.id))).hexdigest()
        session.key = session_key
        session.refresh_token = refresh
        session.last_updated_date = timezone.now()
        session.save()
        return True
    return False


def login_user(user, access, refresh, request=None):
    client_ip = http_request.get_client_ip(request)
    metadata = http_request.get_device_metadata(request)
    session_key = hashlib.sha256(str.encode(access + str(user.id))).hexdigest()
    Session.objects.create(
        user=user,
        key=session_key,
        ip=client_ip,
        device_family=metadata.device.family,
        device_brand=metadata.device.brand,
        device_model=metadata.device.model,
        os_family=metadata.os.family,
        os_version_string=metadata.os.version_string,
        browser_family=metadata.browser.family,
        browser_version_string=metadata.browser.version_string,
        refresh_token=refresh
    )

