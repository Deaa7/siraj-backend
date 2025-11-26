from django.contrib import admin

from .models import NotesAppendixes


@admin.register(NotesAppendixes)
class NotesAppendixesAdmin(admin.ModelAdmin):
    list_display = ("public_id", "note_id", "created_at", "updated_at")
    search_fields = ("public_id", "note_id__public_id", "note_id__name")
    list_filter = ("created_at", "updated_at")
