import enum
import requests
from hashlib import sha256
from collections import OrderedDict


class TinkoffURLS:
    BASE_URL = 'https://api.cryptocloud.plus'
    V1_INVOICE_CREATE = '/v1/invoice/create'
    V1_INVOICE_INFO = '/v1/invoice/info'


class TinkoffTaxation(enum.Enum):
    OSN = 'osn'
    USN_INCOME = 'usn_income'
    USN_INCOME_OUTCOME = 'usn_income_outcome'
    PATENT = 'patent'
    ENVD = 'envd'
    ESN = 'esn'


class TinkoffReceiptItem:
    # TODO: future implement
    def __init__(self):
        pass


class TinkoffReceipt:
    # TODO: future implement
    def __init__(self,
                 email: str,
                 company_email: str,
                 phone: str = None,
                 taxation: TinkoffTaxation = TinkoffTaxation.OSN):
        pass

    def to_dict(self) -> dict:
        # TODO: future implement
        return dict()


class TinkoffPayments(TinkoffURLS):
    def __init__(self, terminal: str, secret_key: str):
        self._terminal = terminal
        self._secret_key = secret_key

    def create_invoice(self,
                       amount: float,
                       order_id: str,
                       description: str,
                       order_data: dict = None,
                       receipt: TinkoffReceipt = None) -> dict:
        """The method creates payment: the seller receives a link to
        the payment form and must redirect the buyer to it"""
        payload = {
            'Amount': amount,
            'OrderId': order_id,
            'Description': description
        }
        if order_data:
            payload.update({'DATA': order_data})
        if receipt:
            payload.update({'Receipt': receipt.to_dict()})
        return self._call('Init', payload=payload)

    def state(self, payment_id: str) -> dict:
        """Returns the current payment status"""
        return self._call('GetState', payload={'PaymentId': payment_id})

    def _call(self,
              method: str,
              payload: dict) -> dict:
        payload.update({'TerminalKey': self._terminal})

        token = self._get_token(payload)

        response = requests.post(
            f'https://securepay.tinkoff.ru/v2/{method}/',
            json={
                'Token': token,
                **payload,
            },
        )

        if response.status_code != 200:
            raise Exception(
                f'Incorrect HTTP-status code for {method}: {response.status_code}',
            )

        parsed = response.json()
        parsed.update({'token': token})

        return parsed

    def _get_token(self, request: dict) -> str:
        params = {k: v for k, v in request.items() if k not in ['Shops', 'DATA', 'Receipt']}

        params['Password'] = self._secret_key

        sorted_params = OrderedDict(
            sorted((k, v) for k, v in params.items() if k not in ['Shops', 'DATA', 'Receipt']),
        )

        return sha256(''.join(str(value) for value in sorted_params.values()).encode()).hexdigest()


if __name__ == '__main__':
    provider = TinkoffPayments(terminal='1666879796677DEMO', secret_key='keozdjh7x8pz9qg7')
    s = provider.state('2684104732')
    # Card: 4300 0000 0000 0777
    # Date: 1122
    # CVV: 111
