from django.urls import path
from . import views


urlpatterns = [
    path('purchase-offer/<str:offer_public_id>/', views.purchase_offer, name='purchase_offer'),
]