from django.db import models
from users.models import User
from common.models import PublicModel
from publisherOffers.models import PublisherOffers
class PublisherPlans(PublicModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_publisher_plans")
    offer = models.ForeignKey(PublisherOffers, on_delete=models.CASCADE, related_name="offer_publisher_plans")
    plan_expiration_date = models.DateTimeField(null=True, blank=True)
    activation_date = models.DateTimeField(auto_now_add=True , blank=True )
    auto_renew = models.BooleanField(default=False, blank=True)
    
    
    class Meta:
        ordering = ['-activation_date']