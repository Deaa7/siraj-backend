from django.core.validators import  MinValueValidator
from django.db import models
from users.models import User
from exams.models import Exam
from notes.models import Note
from courses.models import Course
from common.models import PublicModel
# Create your models here.

class StudentPremiumContent(PublicModel):
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_premium_content_student')
    type = models.CharField(max_length= 10, default='') # exam , note , course
    content_public_id = models.CharField(max_length= 100, default='', blank=True, null=True)
    exam_id = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True, related_name='student_premium_content_exam')
    note_id = models.ForeignKey(Note, on_delete=models.CASCADE, null=True, blank=True, related_name='student_premium_content_note')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='student_premium_content_course')
    publisher_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='student_premium_content_publisher')
    purchase_date = models.DateTimeField(auto_now_add=True , blank=True , null=True)
    date_of_expiration = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-purchase_date']
        