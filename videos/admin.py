from django.contrib import admin
from .models import Videos
# Register your models here.
class VideosAdmin(admin.ModelAdmin):
    list_display = ['public_id', 'name', 'explanation', 'url', 'publisher_id']
admin.site.register(Videos, VideosAdmin)