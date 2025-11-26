from django.db import models

from users.models import User
# Create your models here.
from django.core.validators import MinLengthValidator, MinValueValidator
from Constants import CITIES
from common.models import PublicModel
class ServicePurchaseHistory(PublicModel):
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='service_purchase_history_user')
    full_name = models.CharField(max_length= 300, default='', validators=[MinLengthValidator(2)])
    user_type = models.CharField(max_length= 50, default='')#student, teacher , team
    phone = models.CharField(max_length= 15, default='', validators=[MinLengthValidator(2)])
    city = models.CharField(max_length= 30, default='حمص', choices=CITIES)
    service_name = models.CharField(max_length= 500, default='', validators=[MinLengthValidator(2)])
    service_price = models.DecimalField(max_digits=10, decimal_places=2,default=0 , blank=True , validators=[MinValueValidator(0)])
    purchase_date = models.DateTimeField(auto_now_add=True , blank=True , null=True)
    

    