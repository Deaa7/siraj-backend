from django.urls import path
from . import views

urlpatterns = [
    path('get-video/<str:public_id>/', views.get_videos, name='get_videos'),
    path('create-video/', views.create_video, name='create_video'),
    path('update-video/<str:public_id>/', views.update_video, name='update_video'),
    path('delete-video/<str:public_id>/', views.delete_video, name='delete_video'),
    path('delete-video-from-bucket/', views.delete_video_from_bucket, name='delete_video_from_bucket'),
    path('get-video-presigned-url/', views.get_video_presigned_url, name='get-video-presigned-url'),
]