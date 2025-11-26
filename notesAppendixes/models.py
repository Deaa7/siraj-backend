from django.db import models

# Create your models here.
from notes.models import Note
from common.models import PublicModel

class NotesAppendixes(PublicModel):
    note_id = models.ForeignKey(Note, on_delete=models.CASCADE)
    MCQ = models.JSONField(default=dict)
    summary = models.TextField(default='', max_length=50000) # markdown format