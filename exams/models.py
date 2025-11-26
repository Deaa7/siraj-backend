from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from Constants import CLASSES, LEVELS, SUBJECT_NAMES
from users.models import User
import uuid
from common.models import PublicModel
# Create your models here.


class Exam(PublicModel):
    name = models.CharField(max_length=255 ,validators=[MinLengthValidator(3 , 'اسم الامتحان يجب ان يكون اطول من 3 حروف')])
    publisher_id = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='exams_publisher', null=True, blank=True)
    units = models.CharField(max_length = 2000 ,default='', validators=[MinLengthValidator(2)])
    Class = models.CharField(max_length = 6 ,choices=CLASSES, default='12')
    subject_name = models.CharField(max_length = 60 ,choices=SUBJECT_NAMES, default='math')
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0 , blank=True , validators=[MinValueValidator(0)])
    number_of_apps = models.IntegerField(default=0 , blank=True , validators=[MinValueValidator(0)])
    number_of_purchases = models.IntegerField(default=0 , blank=True , validators=[MinValueValidator(0)])
    number_of_questions = models.IntegerField(default=0 , blank=True , validators=[MinValueValidator(0)])
    number_of_comments = models.IntegerField(default=0 , blank=True , validators=[MinValueValidator(0)])
    result_avg = models.DecimalField(max_digits=10, decimal_places=2,default=0 , blank=True , validators=[MinValueValidator(0)])
    level = models.CharField(max_length=6 ,default='سهل', choices=LEVELS)
    description = models.TextField(max_length=1000 ,default='', )
    visibility = models.CharField(max_length=10 ,default='public' , blank=True)
    active = models.BooleanField(default=True , blank=True )
    disable_date = models.DateTimeField(null=True, blank=True)
    disabled_by =models.CharField(max_length=50 ,default='' , blank = True , null = True)#publisher, admin
    profit_amount =models.DecimalField(max_digits=10, decimal_places=2,default=0 , blank=True , validators=[MinValueValidator(0)])
    
    class Meta:
        indexes = [
            models.Index(fields=['active' ,'visibility','subject_name','Class', '-created_at']),
            # models.Index(fields=['active' ,'subject_name','Class', '-number_of_likes' ]),
            models.Index(fields=['active' ,'visibility','subject_name','Class', '-number_of_apps' ]),
            models.Index(fields=['active' ,'visibility','subject_name','Class', '-number_of_purchases' ]),
        ]
         
 
    
    