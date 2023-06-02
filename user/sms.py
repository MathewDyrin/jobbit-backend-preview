import requests
from django.conf import settings


class SmsException(Exception):
    pass


class BaseSmsMessage:

    def send(self, *args, **kwargs):
        raise NotImplementedError('Method must be implemented before using')

    def check_status(self, *args, **kwargs):
        raise NotImplementedError('Method must be implemented before using')


class SmsAeroMessage(BaseSmsMessage):

    def __init__(self, signature: str = None, api_key: str = None, email: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signature = signature or getattr(settings, 'SMS_AERO_SIGNATURE ', '')
        self.api_key = api_key or getattr(settings, 'SMS_AERO_API_KEY', '')
        self.email = email or getattr(settings, 'SMS_AERO_EMAIL', '')

    def check_status(self, message_id: str):
        try:
            return requests.get(
                'https://{email}:{api_key}@gate.smsaero.ru/v2/sms/status?id={message_id}'
                .format(email=self.email, api_key=self.api_key, message_id=message_id))
        except requests.exceptions.RequestException as e:
            raise SmsException(e)

    def send(self, number_list: list, text: str):
        if not isinstance(number_list, list):
            raise SmsException('parameter number list is not a list')
        try:
            return requests.get(
                'https://{email}:{api_key}@gate.smsaero.ru/v2/sms/send?{number_list}&text={text}&sign={signature}'
                .format(
                    email=self.email, api_key=self.api_key,
                    number_list=''.join('numbers[]={}&'.format(number) for number in number_list)[:-1],
                    text=text, signature=self.signature))
        except requests.exceptions.RequestException as e:
            raise SmsException(e)


class TelegramSmsMessage:
    @staticmethod
    def send(chat_id: list, text_message: str):
        TG_BOT_TOKEN = getattr(settings, 'TG_BOT_TOKEN', '')
        data = {
            'chat_id': getattr(settings, 'TG_CHAT_ID', ''),
            'text': text_message,
            'parse_mode': 'HTML'
        }
        requests.post(
            f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage',
            json=data
        )


class Smser:
    __mapper__ = {
        'SmsAeroMessage': SmsAeroMessage,
        'TelegramSmsMessage': TelegramSmsMessage
    }

    @classmethod
    def check_status(cls, message_id: str):
        sms_settings = getattr(settings, 'SMS_MESSAGE', '')
        defined_sms_message = sms_settings.get('DEFAULT_SMSER')
        controller = cls.__mapper__.get(defined_sms_message)
        return controller.check_status(message_id)

    @classmethod
    def send(cls, number_list: list, text: str):
        sms_settings = getattr(settings, 'SMS_MESSAGE', '')
        defined_sms_message = sms_settings.get('DEFAULT_SMSER')
        controller = cls.__mapper__.get(defined_sms_message)
        return controller.send(number_list, text)
