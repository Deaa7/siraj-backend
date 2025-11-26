from django.urls import path
from . import views


urlpatterns = [
    path('get-publisher-plan-statistics/', views.get_publisher_plan_statistics, name='get_publisher_plan_statistics'),
    path('update-auto-renew/<str:plan_public_id>/', views.update_auto_renew, name='update_auto_renew'),
]