from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from common.models import PublicModel
from users.models import User

class Post(PublicModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts")
    content = models.TextField(max_length=10000, validators=[MinLengthValidator(2)]) # markdown format
    allowed_comments = models.BooleanField(default=True , blank=True)
    active = models.BooleanField(default=True , blank=True)
    number_of_comments = models.PositiveIntegerField(default=0 , blank=True , validators=[MinValueValidator(0)])
    # number_of_likes = models.PositiveIntegerField(default=0 , blank=True , validators=[MinValueValidator(0)])