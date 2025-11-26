from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from Constants import CITIES, CLASSES, GENDERS, LEVELS, SUBJECT_NAMES
from users.models import User
from exams.models import Exam
from common.models import PublicModel
# Create your models here.

class ExamAppTracking(PublicModel):
    
    exam_id = models.ForeignKey(Exam, on_delete=models.SET_NULL, related_name='exam_app_tracking_exam', null=True, blank=True)
    publisher_id = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='exam_app_tracking_publisher', null=True)
    student_id = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='exam_app_tracking_student', null=True)
    number_of_apps = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])
    result_of_first_app = models.DecimalField(max_digits=10, decimal_places=2,default=1000, blank=True, validators=[MinValueValidator(0)])
    last_app_date = models.DateTimeField(auto_now=True , blank=True)
    result_of_last_app = models.DecimalField(max_digits=10, decimal_places=2,default=0, blank=True, validators=[MinValueValidator(0)])
    highest_score = models.DecimalField(max_digits=10, decimal_places=2,default=0, blank=True, validators=[MinValueValidator(0)])
    lowest_score = models.DecimalField(max_digits=10, decimal_places=2,default=0, blank=True, validators=[MinValueValidator(0)])
    result_average = models.DecimalField(max_digits=10, decimal_places=2,default=0, blank=True)
   
    # number of seconds     
    time_of_first_app = models.IntegerField(default=0, blank=True)
    shortest_time = models.IntegerField(default=0, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=[ 'student_id', '-created_at']),
            models.Index(fields=[ 'publisher_id', '-created_at']),
            models.Index(fields=[ 'exam_id', '-created_at']),
        ]
        