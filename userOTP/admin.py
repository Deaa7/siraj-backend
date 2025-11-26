from django.contrib import admin
from .models import UserOTP

# Register your models here.

@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp_code', 'purpose', 'is_used', 'created_at', 'expire_at']
    list_filter = ['is_used', 'purpose', 'created_at']
    search_fields = ['user__username', 'user__email', 'otp_code']
    readonly_fields = ['created_at', 'otp_code']
    ordering = ['-created_at']
    
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user',)
        }),
        ('معلومات رمز التحقق', {
            'fields': ('otp_code', 'purpose', 'is_used')
        }),
        ('التواريخ', {
            'fields': ('created_at', 'expire_at')
        }),
    )
