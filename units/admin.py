from django.contrib import admin
from .models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = [
        'name',
        'slug',
        'public_id',
        'Class',
        'subject_name',
        'description',
        'created_at',
        'updated_at',
    ]

    # Fields that can be searched
    search_fields = [
        'name',
        'slug',
        'public_id',
        'Class',
        'subject_name',
    ]

    # Fields that can be filtered
    list_filter = [
        'Class',
        'subject_name',
        'created_at',
        'updated_at',
    ]

    # Fields to display in the detail form
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'slug', 'Class', 'subject_name')
        }),
        ('معلومات إضافية', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )

    # Fields that are read-only
    readonly_fields = ['slug', 'public_id', 'created_at', 'updated_at']

    # Number of items per page
    list_per_page = 25

    # Enable date hierarchy
    date_hierarchy = 'created_at'
