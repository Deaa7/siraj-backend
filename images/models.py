from django.db import models
from posts.models import Post
from common.models import PublicModel


class Image(PublicModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.CharField(max_length=400)
 