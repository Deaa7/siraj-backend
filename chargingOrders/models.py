from django.db import models
from django.core.validators import  MinValueValidator
# Create your models here.
from users.models import User
from common.models import PublicModel


class ChargingOrders(PublicModel):
    StatusChoices = [
        ("pending", "قيد المراجعة"),
        ("confirmed", "تم التأكيد"),
        ("cancelled", "تم الإلغاء"),
    ]
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name='charging_orders_user')
    payment_way = models.CharField(max_length= 50, default='')
    payment_photo = models.ImageField(upload_to='charging_orders/payment_photos/', default='' , blank=True)
    status = models.CharField(max_length= 50, default='pending', choices=StatusChoices,  blank  = True)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0 , validators=[MinValueValidator(0)])
    confirmation_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status' , '-created_at']),
        ]
        
        