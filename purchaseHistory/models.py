from django.db import models
from users.models import User
from django.core.validators import MinLengthValidator, MinValueValidator
from Constants import CLASSES, CITIES, GENDERS, SUBJECT_NAMES
from common.models import PublicModel

class PurchaseHistory(PublicModel):
    
    publisher_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='purchase_history_publisher')
    publisher_name = models.CharField(max_length= 300, default='', validators=[MinLengthValidator(2)])
    content_type = models.CharField(max_length= 50, default='')#exam, note, course
    content_id = models.IntegerField(default=0,)
    content_name = models.CharField(max_length= 300, default='', validators=[MinLengthValidator(2)])
    content_class = models.CharField(max_length= 6, choices=CLASSES, default='12')
    content_subject_name = models.CharField(max_length= 60, choices=SUBJECT_NAMES, default='math')
    student_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='purchase_history_student')
    student_name = models.CharField(max_length= 300, default='', validators=[MinLengthValidator(2)])
    student_city = models.CharField(max_length= 50, default='حمص', choices=CITIES)
    student_gender = models.CharField(max_length= 1, default='M', choices=GENDERS)
    student_class = models.CharField(max_length= 6, choices=CLASSES, default='12')
    purchase_date = models.DateTimeField(auto_now_add=True , blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0 , blank=True , validators=[MinValueValidator(0)])
    publisher_profit = models.DecimalField(max_digits=10, decimal_places=2,default=0 , blank=True , validators=[MinValueValidator(0)])
    owner_profit = models.DecimalField(max_digits=10, decimal_places=2,default=0 , blank=True , validators=[MinValueValidator(0)])
    discount_code = models.CharField(max_length= 50, default='-' , blank=True)
    discount_value = models.CharField(max_length= 50, default='0' , blank=True)
 