from django.contrib import admin
from .models import TempUpload
# Register your models here.
class TempUploadAdmin(admin.ModelAdmin):
    list_display = ['name', 'expiration_date']
    
admin.site.register(TempUpload, TempUploadAdmin)