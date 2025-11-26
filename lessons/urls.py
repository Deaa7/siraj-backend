from django.urls import path
from .views import create_lesson, get_lessons



urlpatterns = [
    path('create-lesson/', create_lesson, name='create_lesson'),
    path('get-lessons/<str:course_id>/', get_lessons, name='get_lessons'),
]