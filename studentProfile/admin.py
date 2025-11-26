from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = [
        'user',
        'full_name',
        'phone',
        'get_user_balance',
        'Class',
        "city",
        'school',
        'number_of_done_exams',
        'number_of_read_notes',
        'number_of_completed_courses',
        'created_at'
    ]
    
    def full_name(self, obj):
        return obj.user.full_name
    def phone(self, obj):
        return obj.user.phone
    def city(self, obj):
        return obj.user.city
    
    
    # Fields that can be searched
    search_fields = [
        'full_name',
        'Class',
        'created_at',
    ]
    
    # Fields that can be filtered
    list_filter = [
        'Class',
        'school',
        'created_at',
    ]
    
    # Fields to display in the detail form
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user',)
        }),
        ('المعلومات الأساسية', {
            'fields': ('full_name', 'phone', 'Class', 'school')
        }),
        ('الإحصائيات', {
            'fields': ('number_of_done_exams', 'number_of_read_notes', 'number_of_completed_courses'),
            'classes': ('collapse',)
        }),
    )
    
    # Fields that are read-only
    readonly_fields = []
    
    # Fields to display horizontally
    filter_horizontal = []
    
    # Number of items per page
    list_per_page = 25
    
    # Enable date hierarchy
    # date_hierarchy = 'user__created_at'
    
    # Custom methods for display
    # def get_user_first_name(self, obj):
    #     return obj.user.first_name
    # get_user_first_name.short_description = 'الاسم الأول'
    # get_user_first_name.admin_order_field = 'first_name'
    
    # def get_user_last_name(self, obj):
    #     return obj.user.last_name
    # get_user_last_name.short_description = 'الاسم الأخير'
    # get_user_last_name.admin_order_field = 'last_name'
    
    def get_user_balance(self, obj):
        return f"{obj.user.balance}"
    get_user_balance.short_description = 'الرصيد'
    get_user_balance.admin_order_field = 'user__balance'
    
    # def get_user_email(self, obj):
    #     return obj.user.email
    # get_user_email.short_description = 'البريد الإلكتروني'
    # get_user_email.admin_order_field = 'user__email'
    
    # def get_user_phone(self, obj):
    #     return obj.user.phone
    # get_user_phone.short_description = 'رقم الهاتف'
    # get_user_phone.admin_order_field = 'phone'
    
    # # Custom actions
    # actions = ['reset_statistics', 'mark_as_confirmed']
    
    # def reset_statistics(self, request, queryset):
    #     """Reset all statistics to zero"""
    #     updated = queryset.update(
    #         number_of_done_exams=0,
    #         number_of_read_notes=0,
    #         number_of_completed_courses=0
    #     )
    #     self.message_user(request, f'تم إعادة تعيين إحصائيات {updated} طالب')
    # reset_statistics.short_description = 'إعادة تعيين الإحصائيات'
    
    # def mark_as_confirmed(self, request, queryset):
    #     """Mark selected users as confirmed"""
    #     updated = queryset.update(user__is_account_confirmed=True)
    #     self.message_user(request, f'تم تأكيد حساب {updated} طالب')
    # mark_as_confirmed.short_description = 'تأكيد الحسابات'
    
    # # Customize the form
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     # Make user field read-only when editing existing profile
    #     if obj:
    #         form.base_fields['user'].disabled = True
    #     return form
