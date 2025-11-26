from django.contrib import admin
from .models import ChargingOrders
# Register your models here.

@admin.register(ChargingOrders)
class ChargingOrdersAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name' , 'email', 'phone', 'account_type', 'amount', 'payment_way', 'payment_photo', 'created_at', 'status', 'confirmation_date']

    def email(self, obj):
        return obj.user.email
    
    def phone(self, obj):
        return obj.user.phone
    def full_name(self, obj):
        return obj.user.full_name
    
    def account_type(self, obj):
        return obj.user.account_type
 