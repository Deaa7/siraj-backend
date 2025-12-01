from django.contrib import admin
from .models import Exam


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = [
        'name',
        "public_id",
        "full_name",
        'publisher_id',
        'units',
        'Class',
        'subject_name',
        'price',
        'created_at',
        'updated_at',
        'number_of_apps',
        'number_of_purchases',
        'number_of_questions',
        'number_of_comments',
        'result_avg',
        'level',
        'visibility',
        'active',
        'disable_date',
        'disabled_by',
        'profit_amount',
        'description',
    ]
    def full_name(self, obj):
        name = ""
        if obj.publisher_id.account_type == "teacher":
            name = "الاستاذ " if obj.publisher_id.gender == "M" else "الآنسة " 
            name += obj.publisher_id.full_name
        elif obj.publisher_id.account_type == "team":
            name = "فريق " + obj.publisher_id.team_name
        return name
    
 
    # Fields that can be searched
    search_fields = [
        'name',
        'publisher_id__username',
        'publisher_id__email',
        'units',
        'Class',
        'subject_name',
        'public_id',
    ]
    
    # Fields that can be filtered
    list_filter = [
        'visibility',
        'Class',
        'subject_name',
        'price',
        'created_at',
        'updated_at',
    ]
    
    # Fields to display in the detail form
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('publisher_id'  ,)
        }),
        ('المعلومات الأساسية', {
            'fields': ( 'name' ,'units', 'Class', 'subject_name', 'price')
        }),
        ('الإحصائيات', {
            'fields': ('number_of_apps', 'number_of_purchases', 'number_of_questions', 'number_of_comments', 'result_avg', 'level', 'profit_amount'),
            'classes': ('collapse',)
        }),
        ('معلومات إضافية', {
            'fields': ('description', 'disable_date', 'disabled_by'),
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
    date_hierarchy = 'created_at'
    

 
