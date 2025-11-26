from django.core.validators import MinLengthValidator
from django.db import models
from users.models import User
from notes.models import Note
from common.models import PublicModel
# Create your models here.
class NoteReadTracking(PublicModel):
    note_id = models.ForeignKey(Note, on_delete=models.DO_NOTHING, related_name='note_read_tracking_note')
    publisher_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='note_read_tracking_publisher')
    student_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='note_read_tracking_student')
    first_read_date = models.DateTimeField(auto_now_add=True , blank=True , null=True)
    last_read_date = models.DateTimeField(auto_now=True , blank=True , null=True)
    number_of_reads = models.IntegerField(default=0, blank=True)
    
    class Meta:
        verbose_name = "Note Read Tracking"
        verbose_name_plural = "Note Read Trackings"
        indexes = [
        models.Index(fields=[ 'student_id', '-created_at']),
        models.Index(fields=[ 'publisher_id', '-created_at']),
        models.Index(fields=[ 'note_id', '-created_at']),
     ]
    