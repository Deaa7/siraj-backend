from django.contrib import admin

from .models import Reports


@admin.register(Reports)
class ReportsAdmin(admin.ModelAdmin):
    list_display = (
        "public_id",
        "full_name",
        "reported_user_full_name",
        "reported_content_type",
        "verified",
        "report_date",
    )
    list_filter = ("verified", "reported_content_type", "report_date")
    search_fields = ("full_name", "reported_user_full_name", "public_id")
