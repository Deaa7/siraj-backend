from django.contrib import admin
from .models import Notifications
# Register your models here.


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = (
        "public_id",
        "receiver_id",
        "source_type",
        "title",
        "read",
        "created_at",
    )
    list_filter = ("read", "source_type", "created_at")
    search_fields = ("public_id", "title", "receiver_id__full_name")