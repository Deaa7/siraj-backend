 
from django.contrib import admin
from .models import User
# Register your models here.


class UserAdmin(admin.ModelAdmin):
  
    # Display fields in list view
    list_display = (
        'username',
        'account_type',
        'full_name',
        'email',
        'is_account_confirmed',
        'balance',
        'created_at',
        'is_banned',
        'banning_reason',
        'uuid',
    )
    
    # Fields that can be clicked to sort
    sortable_by = (
        'email',
        'created_at', 'balance')
    
    # Filters in the right sidebar
    list_filter = (
        'is_banned',
        'is_account_confirmed',
        'account_type',
        'created_at',
    )
    
    # Search functionality
    search_fields = (
        'username',
        'email',
        'uuid',
    )
    
    
admin.site.register(User,UserAdmin)