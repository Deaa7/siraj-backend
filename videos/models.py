from django.db import models

# Create your models here.
from users.models import User
from common.models import PublicModel
class Videos(PublicModel):
    publisher_id = models.ForeignKey(User, on_delete=models.SET_NULL , null=True)
    video_url = models.CharField(max_length= 300, default='')
    file_size = models.IntegerField(default=0)
    file_unique_name = models.CharField(max_length= 400, default='')
    video_explanation = models.TextField(default='' , max_length=40000 , blank=True)