from django.db import models
from django.core.validators import MinValueValidator
from common.models import PublicModel
# Create your models here.

class   PublisherOffers(PublicModel):
    
    offer_name = models.CharField(max_length= 100, default='')
    offer_price = models.DecimalField(max_digits=10, decimal_places=2,default=0 , blank=True )
    offer_for = models.CharField(max_length=20 , choices=[("teacher", "teacher"), ("team", "team")] , default="teacher")
    number_of_exams = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    number_of_notes = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    number_of_courses = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True , blank=True)