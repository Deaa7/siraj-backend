from django.contrib import admin
from .models import ServicePurchaseHistory
# Register your models here.
class ServicePurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'full_name', 'user_type', 'phone', 'city', 'service_name', 'service_price', 'purchase_date']
    
admin.site.register(ServicePurchaseHistory, ServicePurchaseHistoryAdmin)