from rest_framework import serializers
from .models import Transaction, SubscriptionPlan, UserRole


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = (
            'D1_PRO_SUB', 'W1_PRO_SUB', 'M1_PRO_SUB', 'M3_PRO_SUB',
            'currency'
        )
        read_only_fields = (
            'D1_PRO_SUB', 'W1_PRO_SUB', 'M1_PRO_SUB', 'M3_PRO_SUB',
            'currency'
        )


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id', 'status', 'pay_url', 'purpose', 'invoice_id', 'currency',
            'payment_type', 'amount', 'date', 'type'
        )
        read_only_fields = (
            'id', 'status', 'pay_url', 'purpose', 'invoice_id', 'currency',
            'payment_type', 'amount', 'date', 'type'
        )


class TransactionCreateSerializer(serializers.Serializer):
    PaymentTypeChoices = [
        "SINGULAR"  # , "RECURRENT"
    ]

    SubLevelChoices = [
        "STANDARD", "PRO", "ULTIMA"
    ]

    AcquiringTypeChoices = [
        "CRYPTO", "STRIPE"  # , "BANKING"
    ]

    PeriodChoices = [
        'D1', 'W1', 'M1', 'M3'
    ]

    # payment_type = serializers.ChoiceField(choices=PaymentTypeChoices, required=True)
    # promo_code = serializers.CharField(required=False)
    sub_level = serializers.ChoiceField(choices=SubLevelChoices, required=True)
    acquiring_type_provider = serializers.ChoiceField(choices=AcquiringTypeChoices, required=True)
    period = serializers.ChoiceField(choices=PeriodChoices, required=True)
    user_role = serializers.ChoiceField(choices=UserRole.choices)

    def validate(self, attrs):
        data = super().validate(attrs)
        # TODO: validate promo_code
        return data
