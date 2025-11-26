from django.db import models
from users.models import User
from common.models import PublicModel
# Create your models here.

class Reports(PublicModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_user')
    full_name = models.CharField(max_length= 300, default='')
    reported_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_reported_user')
    reported_user_full_name = models.CharField(max_length= 300, default='')
    report_date = models.DateTimeField(auto_now_add=True , blank=True )
    report_description = models.TextField(max_length= 1000, default='')
    reported_content_type = models.CharField(max_length= 50, default='')#exam, note, course, post
    verified = models.BooleanField(default=False, blank=True)
  