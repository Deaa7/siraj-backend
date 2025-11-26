from django.contrib import admin
from .models import StudentPremiumContent
# Register your models here.
@admin.register(StudentPremiumContent)
class StudentPremiumContentAdmin(admin.ModelAdmin):
    list_display = ["public_id", "student_id","type" ,"exam_id", "note_id", "course_id", "publisher_id", "purchase_date", "date_of_expiration"]
    