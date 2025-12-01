from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from users.models import User
from Constants import CLASSES, SUBJECT_NAMES, LEVELS
from common.models import PublicModel


class Course(PublicModel):
    name = models.CharField(max_length= 300, validators=[MinLengthValidator(2)])
    subject_name = models.CharField(max_length= 60, choices=SUBJECT_NAMES ,default='math')
    Class = models.CharField(max_length= 6, choices=CLASSES ,default='12')
    publisher_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='courses_publisher')
    what_you_will_learn = models.TextField(max_length= 6000, default='')
    description = models.TextField(max_length= 1000, default='', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0 , blank=True , validators=[MinValueValidator(0)])
    level = models.CharField(max_length= 20, default='سهل',  choices=LEVELS)
    number_of_enrollments = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])
    number_of_comments = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])
    number_of_purchases = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])
    number_of_completions = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])
    number_of_lessons = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True , blank=True )
    disable_date = models.DateTimeField(null=True, blank=True)
    disabled_by = models.CharField(max_length=50 ,default='' , blank = True , null = True)#publisher, admin
    course_image = models.CharField(max_length= 300, default='' , blank = True)
    estimated_time = models.IntegerField(default=0, blank=True)
    profit_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0 , blank=True , validators=[MinValueValidator(0)])
    
    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        indexes = [
            models.Index(fields=['active' , 'subject_name','Class', '-created_at']),
            models.Index(fields=['active' ,'subject_name','Class', '-number_of_enrollments' ]),
            # models.Index(fields=['active' ,'subject_name','Class', '-number_of_likes' ]),
            models.Index(fields=['active' ,'subject_name','Class', '-number_of_purchases' ]),
        ]
    
    def __str__(self):
        return self.name
    
    
    
    