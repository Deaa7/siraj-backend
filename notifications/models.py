from django.db import models
from users.models import User
from django.core.validators import MinLengthValidator
from common.models import PublicModel

class Notifications(PublicModel):
    
    receiver_id = models.ForeignKey(User , related_name='notifications_receiver' , on_delete=models.CASCADE)
    source_type = models.CharField(max_length= 70, default='')#exam, note, course, post
    source_id = models.CharField(max_length= 100, default='', blank=True )
    title = models.CharField(max_length= 100, default='', validators=[MinLengthValidator(2)])
    content = models.TextField(max_length= 1000, default='', validators=[MinLengthValidator(2)])
    read = models.BooleanField(default=False, blank=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"