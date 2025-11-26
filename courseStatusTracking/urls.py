from django.urls import path
from . import views


urlpatterns = [
    # students 
    path('course-status-tracking-cards/<str:public_student_id>/', views.get_course_status_tracking_cards, name='get_course_status_tracking_cards'),
    path('create-course-status-tracking/<str:course_public_id>/', views.create_course_status_tracking, name='create_course_status_tracking'),
  

]