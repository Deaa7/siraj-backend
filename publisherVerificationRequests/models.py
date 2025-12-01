from django.db import models

from users.models import User
from django.core.validators import MinLengthValidator
from common.models import PublicModel
class PublisherVerificationRequests(PublicModel):
    
    publisher_id = models.ForeignKey(User, on_delete=models.CASCADE)
    # name = models.CharField(max_length= 300, default='', validators=[MinLengthValidator(2, "يجب ألا يكون الاسم أقصر من حرفين")])
    # phone = models.CharField(max_length= 15, default='')
    # email = models.EmailField(max_length= 255, default='')
    image1 = models.ImageField(upload_to='publisher_verification_requests/images/', default='')
    image2 = models.ImageField(upload_to='publisher_verification_requests/images/', default='')
    status = models.CharField(max_length= 40, choices=[("pending", "جاري التحقق"), ("approved", "تم التحقق"), ("rejected", "مرفوض")], default="pending")
    processed_at = models.DateTimeField(null=True, blank=True)
    
     