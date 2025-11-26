from django.db import models
from users.models import User
from django.core.validators import MinValueValidator, MinLengthValidator
from common.models import PublicModel
class Transactions(PublicModel):
    
    TRANSACTION_TYPE_CHOICES = [
        ("withdraw", "withdraw"),
        ("purchase", "purchase"),
        ("charge", "charge"),
        ("bonus", "bonus"),
        ("penalty", "penalty"),
    ]
    
    TRANSACTION_STATUS_CHOICES = [
        ("pending", "pending"),
        ("completed", "completed"),
        ("failed", "failed"),
        ("cancelled", "cancelled"),
    ]   
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL , null=True)
    full_name = models.CharField(max_length= 300, default='' , validators=[MinLengthValidator(2, "يجب ألا يكون الاسم أقصر من حرفين")])
    transaction_type = models.CharField(max_length= 50, choices=TRANSACTION_TYPE_CHOICES, default='purchase')
    transaction_status = models.CharField(max_length= 50, choices=TRANSACTION_STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0 )
    balance_before = models.DecimalField(max_digits=10, decimal_places=2,default=0 , validators=[MinValueValidator(0)])
    balance_after = models.DecimalField(max_digits=10, decimal_places=2,default=0 , validators=[MinValueValidator(0)])
 