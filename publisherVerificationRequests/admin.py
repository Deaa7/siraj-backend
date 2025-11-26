from django.contrib import admin

# models
from .models import PublisherVerificationRequests

# Register your models here.

@admin.register(PublisherVerificationRequests)
class PublisherVerificationRequestsAdmin(admin.ModelAdmin):
    list_display = [
        "publisher_id",
        "name",
        "phone",
        "email",
        "status",
        "processed_at",
        "created_at",
    ]
   
    