from django.contrib import admin
from .models import ExamAppTracking


@admin.register(ExamAppTracking)
class ExamAppTrackingAdmin(admin.ModelAdmin):
    list_display = (
        'exam_id',
        'publisher_id',
        'student_id',
        'number_of_apps',
        'result_of_last_app',
        'last_app_date',
    )
    # search_fields = (
    #     'exam_id__name',
    #     'exam_id__public_id',
    #     'student_id__full_name',
    #     'student_id__uuid',
    #     'publisher_id__full_name',
    #     'publisher_id__uuid',
    # )
    # list_filter = ('exam_id__subject_name', 'exam_id__Class', 'publisher_id')
