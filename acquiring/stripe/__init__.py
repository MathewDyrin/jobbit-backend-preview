import requests
from dataclasses import dataclass
from typing import Optional, List


class StripeURLS:
    BASE_URL = 'https://api.stripe.com'
    V1_INVOICE_CREATE = '/v1/payment_links'
    V1_INVOICE_INFO = '/v1/payment_links/{id}'


@dataclass
class StripeLineItems:
    price: str
    quantity: int


@dataclass
class StripeInvoice:
    pay_url: str
    currency: str
    id: str


@dataclass
class StripeRequestError:
    code: str
    doc_url: str
    message: str
    param: str
    request_log_url: str
    type: str


@dataclass
class StripeRequestResult:
    status: bool
    http_code: int
    struct: Optional[StripeInvoice] = None
    error: Optional[StripeRequestError] = None


class StripePayments(StripeURLS):
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._headers = self._generate_base_headers()

    def _generate_base_headers(self):
        _headers = {
            'Authorization': f'Bearer {self._api_key}'
        }
        return _headers

    def create_invoice(self, line_items: List[StripeLineItems]) -> StripeRequestResult:
        data = {
            'line_items[0][price]': line_items[0].price,
            'line_items[0][quantity]': line_items[0].quantity,
        }

        url = self.BASE_URL + self.V1_INVOICE_CREATE
        response = requests.post(url, data=data, headers=self._headers)

        if response.status_code == 200:
            invoice = StripeInvoice(
                id=response.json().get('id'),
                currency=response.json().get('currency'),
                pay_url=response.json().get('url')
            )
            result = StripeRequestResult(
                status=True,
                http_code=response.status_code,
                struct=invoice
            )
            return result
        else:
            err = response.json().get('error')
            error = StripeRequestError(
                code=err['code'],
                message=err['message'],
                doc_url=err['doc_url'],
                param=err['param'],
                type=err['type'],
                request_log_url=err['request_log_url']
            )
            result = StripeRequestResult(
                status=True,
                http_code=response.status_code,
                error=error
            )
            return result

    def invoice_status(self, link_id: str) -> StripeRequestResult:
        url = self.BASE_URL + self.V1_INVOICE_INFO.format(id=link_id)
        response = requests.get(url, headers=self._headers)

        if response.status_code == 200:
            invoice = StripeInvoice(
                id=response.json().get('id'),
                currency=response.json().get('currency'),
                pay_url=response.json().get('url')
            )
            result = StripeRequestResult(
                status=True,
                http_code=response.status_code,
                struct=invoice
            )
            return result
        else:
            err = response.json().get('error')
            error = StripeRequestError(
                code=err['code'],
                message=err['message'],
                doc_url=err['doc_url'],
                param=err['param'],
                type=err['type'],
                request_log_url=err['request_log_url']
            )
            result = StripeRequestResult(
                status=True,
                http_code=response.status_code,
                error=error
            )
            return result


def test_create_invoice(stripe: StripePayments, price: str, quantity: int) -> StripeRequestResult:
    line_items = StripeLineItems(price=price, quantity=quantity)
    invoice = stripe.create_invoice(line_items=[line_items])
    return invoice


def test_invoice_status(stripe: StripePayments, link_id: str) -> StripeRequestResult:
    return stripe.invoice_status(link_id=link_id)


def test_positive_case():
    stripe = StripePayments(api_key='sk_test_4eC39HqLyjWDarjtT1zdp7dc')
    invoice = test_create_invoice(stripe=stripe, price='price_1NJnUg2eZvKYlo2CNaH0xTNU', quantity=1)
    invoice_status = test_invoice_status(stripe, link_id=invoice.struct.id)

    print(invoice)
    print(invoice_status)


def test_bad_case():
    stripe = StripePayments(api_key='sk_test_4eC39HqLyjWDarjtT1zdp7dc')
    invoice = test_create_invoice(stripe=stripe, price='price_1NJnUg2eZvKYlo2CNaH0xTNU', quantity=0)
    invoice_status = test_invoice_status(stripe, link_id='HOLABOLA')

    print(invoice)
    print(invoice_status)


if __name__ == '__main__':
    # test_positive_case()
    # print()
    # print('='*30)
    # print()
    # test_bad_case()
    # Card number: 4242424242424242
    stripe = StripePayments(api_key='sk_test_4eC39HqLyjWDarjtT1zdp7dc')
    print(test_invoice_status(stripe=stripe, link_id='plink_1NPkYf2eZvKYlo2C6NQfN76I'))
