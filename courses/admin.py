from django.contrib import admin
from .models import Course
# Register your models here.

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'publisher_id', 'Class', 'subject_name', 'level', 'price', 'number_of_purchases' ,"profit_amount"]
