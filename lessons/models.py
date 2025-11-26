from django.db import models
from common.models import PublicModel
from courses.models import Course
from django.core.validators import MinLengthValidator


class Lessons(PublicModel):
   
    TYPE_CHOICES = [
        ('video', 'Video'),
        ('exam', 'Exam'),
        ('note', 'Note'),
    ]
   
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
   
    lesson_name = models.CharField(max_length= 300, default='' , validators=[MinLengthValidator(2)])
   
    lesson_type = models.CharField(max_length= 50, default='', choices=TYPE_CHOICES)
   
    content_public_id = models.CharField(max_length= 150, default='', blank=True, null=True)
    
    