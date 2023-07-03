import uuid
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.utils.translation import gettext_lazy as _
from user.models import User
# from toolkit.locale.lang import t


class Currency(models.TextChoices):
    # fiat
    RUB = 'RUB', _('RUB')
    UAH = 'UAH', _('UAH')
    TRY = 'TRY', _('TRY')
    KZT = 'KZT', _('KZT')
    EUR = 'EUR', _('EUR')
    USD = 'USD', _('USD')
    CNY = 'CNY', _('CNY')


class ProSubscriptionPlan(models.Model):
    D1_PRO_SUB = models.FloatField(null=False, blank=False, default=100)
    W1_PRO_SUB = models.FloatField(null=False, blank=False, default=100)
    M1_PRO_SUB = models.FloatField(null=False, blank=False, default=100)
    M3_PRO_SUB = models.FloatField(null=False, blank=False, default=100)

    class Meta:
        abstract = True


class SubscriptionPlan(ProSubscriptionPlan, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency = models.CharField(max_length=6, unique=True, null=False, blank=False, choices=Currency.choices)

    def __str__(self):
        return f"Subscription Plan: {self.currency}"


class TransactionPurpose(models.TextChoices):
    # 1 Day
    D1_PRO_SUB = 'D1_PRO_SUB', _('D1_PRO_SUB')
    # 1 Week
    W1_PRO_SUB = 'W1_PRO_SUB', _('W1_PRO_SUB')
    # 1 Month
    M1_PRO_SUB = 'M1_PRO_SUB', _('M1_PRO_SUB')
    # 3 Months
    M3_PRO_SUB = 'M3_PRO_SUB', _('M3_PRO_SUB')


def is_valid_transaction_purpose(sub_level: str, period: str):
    key = f"{period}_{sub_level}_SUB"
    try:
        TransactionPurpose(key)
        return key
    except ValueError:
        return None


def retreive_purpose_obj_prop(sub_plan: SubscriptionPlan, purpose: str):
    __map = {
        'D1_PRO_SUB': sub_plan.D1_PRO_SUB,
        'W1_PRO_SUB': sub_plan.W1_PRO_SUB,
        'M1_PRO_SUB': sub_plan.M1_PRO_SUB,
        'M3_PRO_SUB': sub_plan.M3_PRO_SUB,
    }
    return __map.get(purpose, None)


def get_timedelta(period: str):
    __map = {
        'D1': timezone.timedelta(days=1),
        'W1': timezone.timedelta(weeks=1),
        'M1': relativedelta(months=1),
        'M3': relativedelta(months=3),
    }
    return __map.get(period, None)


def purpose_translate(purpose, request):
    __map = {
        # 'D1_PRO_SUB': t('transaction.D1_PRO_SUB', request),
        # 'W1_PRO_SUB': t('transaction.W1_PRO_SUB', request),
        # 'M1_PRO_SUB': t('transaction.M1_PRO_SUB', request),
        # 'M3_PRO_SUB': t('transaction.M3_PRO_SUB', request),

        'D1_PRO_SUB': '1 Day Subscription',
        'W1_PRO_SUB': '1 Week Subscription',
        'M1_PRO_SUB': '1 Month Subscription',
        'M3_PRO_SUB': '3 Months Subscription',

    }
    return __map.get(purpose, None)


class TransactionStatus(models.TextChoices):
    CREATED = 'CREATED', _('CREATED')
    PAID = 'PAID', _('PAID')
    PARTIAL = 'PARTIAL', _('PARTIAL')
    CANCELED = 'CANCELED', _('CANCELED')


class PaymentType(models.TextChoices):
    RECURRENT = 'RECURRENT', _('RECURRENT')
    SINGULAR = 'SINGULAR', _('SINGULAR')


class AcquiringProviderType(models.TextChoices):
    CRYPTO = 'CRYPTO', _('CRYPTO')
    STRIPE = 'STRIPE', _('STRIPE')


class TransactionType(models.TextChoices):
    DEPOSIT = 'DEPOSIT', _('DEPOSIT')
    WITHDRAWAL = 'WITHDRAWAL', _('WITHDRAWAL')


class UserRole(models.TextChoices):
    CLIENT = 'CLIENT'
    EXECUTOR = 'EXECUTOR'


class Transaction(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    status = models.CharField(max_length=10, null=True, blank=True, choices=TransactionStatus.choices)
    pay_url = models.URLField(blank=True, null=True)
    invoice_id = models.CharField(max_length=56)
    currency = models.CharField(max_length=7, null=False, choices=Currency.choices)
    payment_type = models.CharField(max_length=10, null=False, choices=PaymentType.choices)
    purpose = models.CharField(max_length=30, null=False, choices=TransactionPurpose.choices)
    amount = models.FloatField(null=False)
    date = models.DateTimeField(null=False, default=timezone.now)
    provider = models.CharField(max_length=30, null=False, choices=AcquiringProviderType.choices)
    type = models.CharField(max_length=10, null=True, blank=True, choices=TransactionType.choices)

    # User
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    user_role = models.CharField(
        max_length=99,
        choices=UserRole.choices
    )

    # may need to expire date

    class Meta:
        ordering = ['-date']


def force_cancel_active_invoices(user):
    transactions = Transaction.objects.filter(user=user).filter(status=TransactionStatus.CREATED)
    for item in transactions:
        item.status = TransactionStatus.CANCELED
        item.pay_url = None
        item.save()


def has_partial_invoices(user):
    transactions = Transaction.objects.filter(user=user).filter(status=TransactionStatus.PARTIAL).first()
    if transactions:
        return True, transactions
    return False, None


class Rate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base = models.CharField(max_length=7, null=False, choices=Currency.choices)
    quote = models.CharField(max_length=7, null=False, choices=Currency.choices)
    rate = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"{self.base} / {self.quote}"
