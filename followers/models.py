from django.db import models
from users.models import User
from common.models import PublicModel
# Create your models here.
class Followers(PublicModel):
    follower_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_follower')
    followed_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_followed')
    