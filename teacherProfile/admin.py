from django.contrib import admin
from .models import TeacherProfile


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = [
        'user',
        'full_name',
        'get_user_balance',
        'university',
        'Class',
        'number_of_exams',
        'number_of_notes',
        'number_of_courses',
        'number_of_followers',
        'verified',
        'get_user_email',
        'get_user_phone',
    ]
    
    # Fields that can be searched
    search_fields = [
        'full_name',
        'user__email',
        'user__phone',
        'university',
        'Class',
        'studying_subjects',
        'address',
    ]
    
    # Fields that can be filtered
    list_filter = [
        'verified',
        'university',
        'Class',
        'user__city',
        'user__gender',
        'user__is_account_confirmed',
        'user__created_at',
    ]
    
    # Fields to display in the detail form
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user',)
        }),
        ('المعلومات الأساسية', {
            'fields': ('studying_subjects', 'university', 'address', 'Class')
        }),
        ('الإحصائيات', {
            'fields': ('number_of_exams', 'number_of_notes', 'number_of_courses', 'number_of_followers'),
            'classes': ('collapse',)
        }),
        ('وسائل التواصل الاجتماعي', {
            'fields': ('telegram_link', 'whatsapp_link', 'instagram_link', 'facebook_link', 'x_link', 'linkedin_link'),
            'classes': ('collapse',)
        }),
        ('معلومات إضافية', {
            'fields': ('verified', 'bio', 'years_of_experience'),
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
    date_hierarchy = 'user__created_at'
    
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
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'البريد الإلكتروني'
    get_user_email.admin_order_field = 'user__email'
    
    def get_user_phone(self, obj):
        return obj.user.phone
    get_user_phone.short_description = 'رقم الهاتف'
    get_user_phone.admin_order_field = 'user__phone'
    
    def full_name(self, obj):
        name = ""
        if obj.user.account_type == "teacher":
            name = "الاستاذ " if obj.user.gender == "M" else "الآنسة " 
            name += obj.user.full_name
        elif obj.user.account_type == "team":
            name = "فريق " + obj.user.team_name
        return name
    
