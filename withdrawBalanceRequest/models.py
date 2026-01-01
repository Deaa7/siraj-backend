from django.db import models
from Constants import CITIES
# Create your models here.
from users.models import User

from common.models import PublicModel

class WithdrawBalanceRequest(PublicModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length= 300, default='')
    email = models.EmailField(max_length= 255, default='')
    phone = models.CharField(max_length= 15, default='')
    city = models.CharField(max_length= 50, default='' ,choices=CITIES)
    original_balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    wanted_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    confirmed = models.BooleanField(default=False ,  blank=True)
    confirmation_date_time = models.DateTimeField(null=True, blank=True)
    payment_way = models.CharField(max_length= 200, default='')
    meta_data = models.CharField(max_length= 200, default='' , null=True, blank=True) # may be shamcash-code , syriatel code ,or some important data for sending money 
    