from user_agents import parse
from django.http.request import HttpRequest
from django.contrib.auth import get_user_model


User = get_user_model()


class Device:
    def __init__(self, family, brand, model):
        self.family = family
        self.brand = brand
        self.model = model


class Os:
    def __init__(self, family, version_string):
        self.family = family
        self.version_string = version_string


class Browser:
    def __init__(self, family, version_string):
        self.family = family
        self.version_string = version_string


class UserDeviceMeta:
    def __init__(self, device: Device, os: Os, browser: Browser):
        self.device = device
        self.os = os
        self.browser = browser


def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_metadata(request: HttpRequest) -> UserDeviceMeta:
    user_agent = parse(request.headers.get('User-Agent'))
    device = Device(user_agent.device.family, user_agent.device.brand, user_agent.device.model)
    os = Os(user_agent.os.family, user_agent.os.version_string)
    browser = Browser(user_agent.browser.family, user_agent.browser.version_string)
    return UserDeviceMeta(device, os, browser)
