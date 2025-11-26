from django.contrib import admin
from .models import PublisherPlans
# Register your models here.
@admin.register(PublisherPlans)
class TeacherPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'offer', 'plan_expiration_date', 'activation_date', 'auto_renew']
    