import requests
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Union


class CryptoCloudExceptions(Exception):
    pass


class CryptoCloudCurrency(Enum):
    USD = 'USD'
    RUB = 'RUB'
    EUR = 'EUR'
    GBP = 'GBP'


class CryptoCloudPaymentStatus(Enum):
    CREATED = 'created'
    PAID = 'paid'
    PARTIAL = 'partial'
    CANCELED = 'canceled'


class CryptoCloudURLS:
    BASE_URL = 'https://api.cryptocloud.plus'
    V1_INVOICE_CREATE = '/v1/invoice/create'
    V1_INVOICE_INFO = '/v1/invoice/info'


@dataclass
class CryptoCloudInvoice:
    status: str
    pay_url: str
    invoice_id: str
    currency: str
    order_id: str


@dataclass
class CryptoCloudInvoiceStatus:
    status: str
    status_invoice: CryptoCloudPaymentStatus = None
    error: str = None


@dataclass
class CryptoCloudRequestResult:
    status: bool
    http_code: int
    struct: Optional[Union[CryptoCloudInvoice, CryptoCloudInvoiceStatus]] = None


@dataclass
class CryptoCloudPostback:
    status: str
    invoice_id: str
    amount_crypto: float
    currency: str
    order_id: str = None
    token: str = None


class CryptoCloudPayments(CryptoCloudURLS):
    def __init__(self, api_key: str, shop_id: str):
        self._api_key = api_key
        self._shop_id = shop_id
        self._headers = self._generate_base_headers()

    def _generate_base_headers(self):
        _headers = {
            'Authorization': f'Token {self._api_key}'
        }
        return _headers

    def create_invoice(self,
                       amount: float,
                       order_id: str,
                       currency: CryptoCloudCurrency = None,
                       customer_email: str = None) -> CryptoCloudRequestResult:
        data = {
            'shop_id': self._shop_id,
            'amount': amount,
            'order_id': order_id
        }

        if currency:
            data.update({'currency': currency.value})

        if customer_email:
            data.update({'email': customer_email})

        url = self.BASE_URL + self.V1_INVOICE_CREATE
        response = requests.post(url, data=data, headers=self._headers)

        if response.status_code == 200:
            invoice = CryptoCloudInvoice(
                status=response.json().get('status'),
                pay_url=response.json().get('pay_url'),
                invoice_id=response.json().get('invoice_id'),
                currency=response.json().get('currency'),
                order_id=response.json().get('order_id')
            )
            result = CryptoCloudRequestResult(
                status=True,
                http_code=response.status_code,
                struct=invoice
            )
        else:
            result = CryptoCloudRequestResult(
                status=True,
                http_code=response.status_code
            )
        return result

    def invoice_status(self, invoice_id: str) -> CryptoCloudRequestResult:
        url = self.BASE_URL + self.V1_INVOICE_INFO + f'?uuid=INV-{invoice_id}'
        response = requests.get(url, headers=self._headers)

        if response.status_code == 200:
            invoice_status_ops = CryptoCloudPaymentStatus(response.json().get('status_invoice'))
            invoice_status = CryptoCloudInvoiceStatus(
                status=response.json().get('status'),
                status_invoice=invoice_status_ops
            )
            result = CryptoCloudRequestResult(
                status=True,
                http_code=response.status_code,
                struct=invoice_status
            )
        else:
            invoice_status = CryptoCloudInvoiceStatus(
                status=response.json().get('status'),
                error=response.json().get('error')
            )
            result = CryptoCloudRequestResult(
                status=True,
                http_code=response.status_code,
                struct=invoice_status
            )
        return result
