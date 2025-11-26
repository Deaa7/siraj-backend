from django.contrib import admin
from .models import TeamProfile


@admin.register(TeamProfile)
class TeamProfileAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = [
        'user',
        # 'get_user_first_name',
        'team_name',
        'get_user_balance',
        'leader_name',
        'number_of_exams',
        'number_of_notes',
        'number_of_courses',
        'number_of_followers',
        'verified',
        'get_user_email',
        # 'get_user_phone',
    ]
    
    # Fields that can be searched
    search_fields = [
        # 'user__first_name',
        'team_name',
        'user__email',
        # 'user__phone',
        'leader_name',
        'address',
        'bio',
    ]
    
    # Fields that can be filtered
    list_filter = [
        'verified',
        # 'user__gender',
        # 'user__city',
        'user__is_account_confirmed',
        'user__created_at',
    ]
    
    # Fields to display in the detail form
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user',)
        }),
        ('معلومات الفريق', {
            'fields': ( 'team_name', 'leader_name', 'address', 'bio')
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
            'fields': ('verified', 'years_of_experience'),
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
    
    def team_name(self, obj):
        return obj.user.team_name
    team_name.short_description = 'اسم الفريق'
    team_name.admin_order_field = 'user__team_name'
    
    def leader_name(self, obj):
        return obj.user.full_name
    leader_name.short_description = 'اسم القائد'
    leader_name.admin_order_field = 'user__full_name'
    
    def get_user_balance(self, obj):
        return f"{obj.user.balance}"
    get_user_balance.short_description = 'الرصيد'
    get_user_balance.admin_order_field = 'user__balance'
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'البريد الإلكتروني'
    get_user_email.admin_order_field = 'user__email'
    
    # def get_user_phone(self, obj):
    #     return obj.user.phone
    # get_user_phone.short_description = 'رقم الهاتف'
    # get_user_phone.admin_order_field = 'user__phone'
