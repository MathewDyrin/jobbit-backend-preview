import base64
import requests


class GoogleAuth:
    def __init__(self, client_id, client_secret, callback_url):
        """ Usage: credentials(client_id, client_secret, callback_url) """
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url

    def login(self):
        return f"https://accounts.google.com/o/oauth2/v2/auth?scope=https://www.googleapis.com/auth/userinfo.email&" \
               f"access_type=offline&include_granted_scopes=true&response_type=code&" \
               f"state=state_parameter_passthrough_value&redirect_uri={self.callback_url}&" \
               f"client_id={self.client_id}"

    def get_tokens(self, code):
        """ Gets the access token from the code given.
        The code can only be used on an active url (callback url)
        meaning you can only use the code once. """
        url = f"https://oauth2.googleapis.com/token?code={code}&" \
              f"client_id={self.client_id}&client_secret={self.client_secret}&" \
              f"redirect_uri={self.callback_url}&grant_type=authorization_code"

        tokens = requests.post(url)
        return tokens.json()

    @staticmethod
    def get_user_data_from_token(access_token):
        """ Gets the user data from an access_token """
        user_data = requests.get(f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}')
        return user_data.json()


class VKAuth:
    def __init__(self, client_id, client_secret, callback_url):
        """ Usage: credentials(client_id, client_secret, callback_url) """
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url

    def login(self):
        return f"https://oauth.vk.com/authorize?client_id={self.client_id}&scope=profile,email,phone" \
               f"&redirect_uri={self.callback_url}&response_type=code"

    def get_tokens(self, code):
        """ Gets the access token from the code given.
        The code can only be used on an active url (callback url)
        meaning you can only use the code once. """
        url = f"https://oauth.vk.com/access_token?client_id={self.client_id}&" \
              f"client_secret={self.client_secret}&code={code}&redirect_uri={self.callback_url}"

        tokens = requests.get(url)
        return tokens.json()


class DiscordAuth:
    def __init__(self, client_id, client_secret, callback_url):
        """ Usage: credentials(client_id, client_secret, callback_url) """
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url

    def login(self):
        """
        Returns a discord auth link, please manually redirect the user then it goes to the callback
        url with the query parameter "code" (example: https://callbackurl/?code=isfd78f2UIRFerf)
        to get the code to use a function called getTokens().

        The code can only be used on an active url (callback url) meaning you can only use the code once
        """
        return f'https://discord.com/oauth2/authorize?client_id={self.client_id}' \
               f'&redirect_uri={self.callback_url}&scope=identify email&response_type=code'

    def get_tokens(self, code):
        """ Gets the access token from the code given.
        The code can only be used on an active url (callback url)
        meaning you can only use the code once. """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.callback_url
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        tokens = requests.post('https://discord.com/api/v8/oauth2/token', data=data, headers=headers)
        return tokens.json()

    def refresh_token(self, refresh_token):
        """ Refreshes access token and access tokens and will return a new set of tokens """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        tokens = requests.post('https://discord.com/api/v8/oauth2/token', data=data, headers=headers)
        return tokens.json()

    @staticmethod
    def get_user_data_from_token(access_token):
        """ Gets the user data from an access_token """
        headers = {
            "Authorization": f'Bearer {access_token}'
        }

        user_data = requests.get('https://discordapp.com/api/users/@me', headers=headers)
        return user_data.json()


class YandexAuth:
    def __init__(self, client_id, client_secret, callback_url):
        """ Usage: credentials(client_id, client_secret, callback_url) """
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = callback_url

    def login(self):
        return f"https://oauth.yandex.ru/authorize?response_type=code&" \
               f"client_id={self.client_id}&" \
               f"redirect_uri={self.callback_url}&" \
               f"scope=login:info login:email"

    def get_tokens(self, code):
        """ Gets the access token from the code given.
        The code can only be used on an active url (callback url)
        meaning you can only use the code once. """
        url = f"https://oauth.yandex.ru/token"
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        tokens = requests.post(url, headers=headers, data=data)
        return tokens.json()

    @staticmethod
    def get_user_data_from_token(access_token):
        """ Gets the user data from an access_token """
        headers = {'Authorization': f'OAuth {access_token}'}
        user_data = requests.get(f'https://login.yandex.ru/info?format=json', headers=headers)
        return user_data.json()
