from django.contrib import admin
from .models import NoteReadTracking


@admin.register(NoteReadTracking)
class NoteReadTrackingAdmin(admin.ModelAdmin):
    list_display = (
        'note_id',
        'publisher_id',
        'student_id',
        'number_of_reads',
        'first_read_date',
        'last_read_date',
    )
    # search_fields = (
    #     'note_id__name',
    #     'note_id__public_id',
    #     'student_id__full_name',
    #     'student_id__uuid',
    #     'publisher_id__full_name',
    #     'publisher_id__uuid',
    # )
    # list_filter = ('note_id__subject_name', 'note_id__Class', 'publisher_id')
