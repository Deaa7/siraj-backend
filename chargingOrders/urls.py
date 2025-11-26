from django.urls import path
from . import views

urlpatterns = [
    path('create-charging-order/', views.create_charging_order.as_view(), name='create-charging-order'),

]