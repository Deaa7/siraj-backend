from django.urls import path
from .views import create_lesson, get_lessons, update_lesson, delete_lesson



urlpatterns = [
    path('create-lesson/<str:course_public_id>/', create_lesson, name='create_lesson'),
    path('get-lessons/<str:course_id>/', get_lessons, name='get_lessons'),
    path('update-lesson/<str:lesson_public_id>/', update_lesson, name='update_lesson'),
    path('delete-lesson/<str:lesson_public_id>/', delete_lesson, name='delete_lesson'),
]