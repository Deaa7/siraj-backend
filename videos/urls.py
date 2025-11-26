from django.urls import path
from . import views

patternUrls = [
    path('videos/get-video/<str:public_id>/', views.get_videos, name='get_videos'),
    path('videos/create-video/', views.create_video, name='create_video'),
    path('videos/update-video/<str:public_id>/', views.update_video, name='update_video'),
    path('videos/delete-video/<str:public_id>/', views.delete_video, name='delete_video'),
]