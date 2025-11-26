from django.contrib import admin

# models
from .models import PurchaseHistory

# Register your models here.
@admin.register(PurchaseHistory)
class PurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = ['content_name', 'content_type', 'content_class', 'price', 'content_subject_name', 'student_name', 'student_city', 'purchase_date', 'publisher_profit', 'discount_code']
  