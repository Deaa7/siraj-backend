from django.contrib import admin

from .models import DiscountCodes

# Register your models here.

@admin.register(DiscountCodes)
class DiscountCodesAdmin(admin.ModelAdmin):
    list_display = ['discount_code', 'discount_for', 'discount_value', 'valid_until', 'active']
