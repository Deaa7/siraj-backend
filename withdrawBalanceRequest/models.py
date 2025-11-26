from django.db import models
from Constants import CITIES
# Create your models here.
from users.models import User

class WithdrawBalanceRequest(models.Model):
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
    shamcash_code = models.CharField(max_length= 80, default='' , null=True, blank=True)
    