import uuid
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.conf import settings
from django.http.request import HttpRequest
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from . import models
from . import serializers
from . import pagination
from user.auth import get_user_id

from acquiring.cryptocloud import CryptoCloudPayments
from acquiring.stripe import StripePayments, StripeLineItems

from chat import services


User = get_user_model()


class SubscriptionPlan(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        currency = 'USD'
        if request.GET.get('currency') and request.GET.get('currency') in [i[0] for i in models.Currency.choices]:
            currency = request.GET.get('currency')

        try:
            sub_plan = models.SubscriptionPlan.objects.get(currency=currency)
            serializer = serializers.SubscriptionPlanSerializer(sub_plan)
            response_data = dict()
            for item in serializer.data:
                if item != 'currency':
                    response_data[item] = {
                        'title': models.purpose_translate(item, request),
                        'price': serializer.data[item],
                        'period': item.split('_')[0],
                        'sub_level': item.split('_')[1],
                    }
            response_data['currency'] = serializer.data['currency']
            return Response(response_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {'err_detail': 'No available subscriptions plans for given currency {0} exist'.format('USD')},
                status=status.HTTP_400_BAD_REQUEST
            )


class Transaction(APIView, pagination.TransactionsListPagination):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.GET.get('role')
        user = request.user
        role_values = models.UserRole.values

        if not role:
            return Response({
                'detail': f'Arg `role` is required. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if role not in role_values:
            return Response({
                'detail': f'Bad value for arg `role`. Possible values: {role_values}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not services.has_required_profile(user, role):
            return Response({
                'detail': 'User has not available profile for this role'
            }, status=status.HTTP_400_BAD_REQUEST)

        transactions = models.Transaction.objects.filter(user=user).filter(user_role=role)
        results = self.paginate_queryset(transactions, request, view=self)
        serializer = serializers.TransactionSerializer(results, many=True)
        for item in serializer.data:
            item['amount'] = "%.2f" % item['amount']
            item['purpose'] = models.purpose_translate(item['purpose'], request)
        return self.get_paginated_response(serializer.data)


class Subscription(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_sub_plan(user, request: HttpRequest, currency='USD'):
        # TODO: only USD subscription plan available
        try:
            sub_plan = models.SubscriptionPlan.objects.get(currency=currency)
            return sub_plan
        except ObjectDoesNotExist:
            return Response(
                {'err_detail': 'No available subscriptions plans for given currency {0} exist'.format('USD')},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        # TODO: validate what products can be retreive by user role
        user = request.user

        serializer = serializers.TransactionCreateSerializer(data=request.data)
        if serializer.is_valid():
            acquiring_type_provider = serializer.validated_data['acquiring_type_provider']
            period = serializer.validated_data['period']
            sub_level = serializer.validated_data['sub_level']
            purpose = models.is_valid_transaction_purpose(sub_level, period)
            role = serializer.validated_data['user_role']

            if not services.has_required_profile(user, role):
                return Response({
                    'detail': 'User has not available profile for this role'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not purpose:
                return Response({'err_detail': 'Bad transaction purpose'}, status=status.HTTP_400_BAD_REQUEST)

            if acquiring_type_provider == 'CRYPTO':
                flag, partial_transaction = models.has_partial_invoices(user)
                if flag:
                    transaction_serializer = serializers.TransactionSerializer(partial_transaction)
                    return Response({'data': transaction_serializer.data}, status=status.HTTP_201_CREATED)

                models.force_cancel_active_invoices(user)
                provider = CryptoCloudPayments(api_key=settings.CCP_API_KEY, shop_id=settings.CCP_SHOP_ID)
                order_id = uuid.uuid4().hex
                # TODO: user this currency at invoices
                # currency = user.base_currency
                sub_plan = self.get_sub_plan(user, request)
                amount = models.retreive_purpose_obj_prop(sub_plan, purpose)

                if not amount:
                    return Response({'err_detail': 'Cannot get invoice amount'}, status=status.HTTP_400_BAD_REQUEST)

                result = provider.create_invoice(
                    amount=amount,
                    order_id=order_id
                )
                if result.status:
                    transaction = models.Transaction.objects.create(
                        id=order_id,
                        status='CREATED',
                        pay_url=result.struct.pay_url,
                        invoice_id=result.struct.invoice_id,
                        currency='USD',
                        payment_type=models.PaymentType.SINGULAR,
                        purpose=purpose,
                        amount=amount,
                        user=user,
                        user_role=role,
                        type=models.TransactionType.DEPOSIT
                    )
                    transaction_serializer = serializers.TransactionSerializer(transaction)
                    return Response({'data': transaction_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'err_detail': result.struct.error}, status=status.HTTP_400_BAD_REQUEST)

            if acquiring_type_provider == 'STRIPE':
                flag, partial_transaction = models.has_partial_invoices(user)
                if flag:
                    transaction_serializer = serializers.TransactionSerializer(partial_transaction)
                    return Response({'data': transaction_serializer.data}, status=status.HTTP_201_CREATED)

                models.force_cancel_active_invoices(user)
                provider = StripePayments(api_key=settings.STRIPE_API_KEY)
                order_id = uuid.uuid4().hex
                # TODO: user this currency at invoices
                # currency = user.base_currency
                sub_plan = self.get_sub_plan(user, request, 'USD')
                amount = models.retreive_purpose_obj_prop(sub_plan, purpose)

                if not amount:
                    return Response({'err_detail': 'Cannot get invoice amount'}, status=status.HTTP_400_BAD_REQUEST)

                line_items = StripeLineItems(price='100', quantity=1)
                invoice = provider.create_invoice(line_items=[line_items])

                print(invoice)

                if invoice.status:
                    transaction = models.Transaction.objects.create(
                        id=order_id,
                        status='CREATED',
                        pay_url=invoice.struct.pay_url,
                        invoice_id=invoice.struct.id,
                        currency=models.Currency.USD,
                        payment_type=models.PaymentType.RECURRENT,
                        purpose=purpose,
                        amount=amount,
                        user=user,
                        user_role=role,
                        type=models.TransactionType.DEPOSIT
                    )
                    transaction_serializer = serializers.TransactionSerializer(transaction)
                    return Response({'data': transaction_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'err_detail': invoice.error}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
