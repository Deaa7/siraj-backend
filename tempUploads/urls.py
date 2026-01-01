
from django.urls import path
from . import views
    
urlpatterns = [
    path('upload-temp-file/', views.upload_temp_file, name='upload-temp-file'),
    path('delete-temp-files/', views.delete_temp_files, name='delete-temp-files'),
    path('delete-single-temp-file/', views.delete_single_temp_file, name='delete-single-temp-file'),
]