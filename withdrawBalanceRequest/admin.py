from django.contrib import admin
from .models import WithdrawBalanceRequest
# Register your models here.
class WithdrawBalanceRequestAdmin(admin.ModelAdmin):
    list_display=["public_id", "user_id", "full_name", "email", "phone", "city", "original_balance", "wanted_amount", "confirmed", "confirmation_date_time", "payment_way", "meta_data"]
    
admin.site.register(WithdrawBalanceRequest, WithdrawBalanceRequestAdmin)