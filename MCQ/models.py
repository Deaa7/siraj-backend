from django.core.validators import MinLengthValidator
from django.db import models
from exams.models import Exam
from common.models import PublicModel

class MCQ(PublicModel):
    CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ]
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.TextField(max_length = 10000, validators=[MinLengthValidator(1)])
    question_image = models.CharField(max_length=400, null=True, blank=True)
    option_A = models.TextField(max_length = 10000, validators=[MinLengthValidator(1)])
    option_B = models.TextField(max_length = 10000, validators=[MinLengthValidator(1)])
    option_C = models.TextField(blank=True, null=True , max_length = 10000, validators=[MinLengthValidator(1)])
    option_D = models.TextField(blank=True, null=True , max_length = 10000, validators=[MinLengthValidator(1)])
    option_E = models.TextField(blank=True, null=True , max_length = 10000, validators=[MinLengthValidator(1)])
    right_answer = models.CharField(max_length=1, choices=CHOICES)
    explanation = models.TextField(blank=True, null=True ,max_length = 10000, validators=[MinLengthValidator(1)])
    is_arabic = models.BooleanField(default=True , blank=True)
 