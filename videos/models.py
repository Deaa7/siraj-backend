from django.db import models

# Create your models here.
from users.models import User
from common.models import PublicModel
class Videos(PublicModel):
    publisher_id = models.ForeignKey(User, on_delete=models.SET_NULL , null=True)
    name = models.CharField(max_length= 500, default='')
    url = models.CharField( max_length = 500 , default = "" )
    explanation = models.TextField(default='' , max_length=40000 , blank=True , null=True)
    
    def __str__(self):
        return self.name