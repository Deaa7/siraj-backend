from django.contrib import admin

# Register your models here.
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["public_id", "name","active", "profit_amount", "subject_name", "Class", "level", "visibility", "get_publisher_name", "number_of_pages", "file_size",  "created_at"]
    search_fields = ["name", "subject_name", "Class", "level", "visibility", "get_publisher_name", "number_of_pages", "file_size", "file_unique_name", "active", "profit_amount"]
    list_editable = ["active", "profit_amount"]
    
    def get_publisher_name(self, obj):
        return obj.publisher_id.full_name
    get_publisher_name.short_description = "Publisher Name"
    get_publisher_name.admin_order_field = "publisher_id__full_name"