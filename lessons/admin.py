from django.contrib import admin
from .models import Lessons
# Register your models here.
class LessonsAdmin(admin.ModelAdmin):
    list_display = ['public_id', 'course_id', 'lesson_type', 'content_public_id']
 
admin.site.register(Lessons, LessonsAdmin)