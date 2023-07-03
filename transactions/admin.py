from django.contrib import admin
from .models import Transaction, SubscriptionPlan, Rate


class SubscriptionPlanAdmin(admin.ModelAdmin):
    # The fields to be used in displaying the SubscriptionPlan model.
    # These override the definitions on the base SubscriptionPlanAdmin
    fieldsets = (
        (None, {'fields': ('currency',)}),
        ('Pro Plan', {'fields': (
            'D1_PRO_SUB', 'W1_PRO_SUB', 'M1_PRO_SUB', 'M3_PRO_SUB',)}),
    )


class TransactionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    # The fields to be used in displaying the Transaction model.
    # These override the definitions on the base TransactionAdmin
    list_display = ('id', 'date', 'user', 'amount', 'invoice_id', 'status', )
    list_filter = ('status',)
    fieldsets = (
        (None, {'fields': ('id', 'date')}),
        ('Invoice info', {'fields': (
            'purpose', 'invoice_id', 'pay_url', 'currency', 'payment_type', 'provider', 'amount', 'type')}),
        ('Status', {'fields': ('status', )}),
        ('User', {'fields': ('user', 'user_role')})
    )

    search_fields = ('user', 'invoice_id')
    filter_horizontal = ()


class RateAdmin(admin.ModelAdmin):
    list_display = ('base', 'quote', 'rate',)
    fieldsets = (
        ('Rate info', {'fields': (
            'base', 'quote', 'rate', )}),
    )


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Rate, RateAdmin)
