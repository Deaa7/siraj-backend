from django.db import models
from users.models import User
from django.core.validators import MinValueValidator
from Constants import CLASSES, SUBJECT_NAMES
from common.models import PublicModel
class StudentSubjectTracking(PublicModel):
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_subject_tracking')
    Class = models.CharField(max_length= 6, choices=CLASSES, default='12')
    subject_name = models.CharField(max_length= 25, choices=SUBJECT_NAMES, default='math')
    number_of_exams = models.IntegerField(default=0, validators=[MinValueValidator(0)] , blank=True, null=True)
    number_of_notes = models.IntegerField(default=0, validators=[MinValueValidator(0)] , blank=True, null=True)
    number_of_courses = models.IntegerField(default=0, validators=[MinValueValidator(0)] , blank=True, null=True)
    
    
    class Meta :
        indexes = [
            models.Index(fields=['student_id', 'Class' , 'subject_name', '-created_at']),
        ]
        verbose_name = "Student Subject Tracking"
        verbose_name_plural = "Student Subject Trackings"