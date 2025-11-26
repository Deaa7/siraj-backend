from django.urls import path
from . import views

urlpatterns = [
    path('resend-otp/', views.resend_otp_view.as_view(), name='resend-otp'),
]
