from django.urls import path
from . import views

urlpatterns = [
    #publishers
    path('increase-number-of-purchases/<str:course_public_id>/', views.increase_number_of_purchases, name='increase_number_of_purchases'),
    path('increase-number-of-enrollments/<str:course_public_id>/', views.increase_number_of_enrollments, name='increase_number_of_enrollments'),
    path('increase-number-of-completions/<str:course_public_id>/', views.increase_number_of_completions, name='increase_number_of_completions'),
    path('change-number-of-comments/<str:course_public_id>/', views.change_number_of_comments, name='change_number_of_comments'),
    path('update-course/<str:course_public_id>/', views.update_course, name='update_course'),
    path('create-course/', views.create_course, name='create_course'),
    path('delete-course/<str:course_public_id>/', views.delete_course, name='delete_course'),
    path('get-course-details-for-dashboard/<str:course_public_id>/', views.get_course_details_for_dashboard, name='get_course_details_for_dashboard'),
    path('get-courses-list-for-dashboard/', views.get_courses_list_for_dashboard, name='get_courses_list_for_dashboard'),
        path('get-course-preview-list/', views.get_course_preview_list, name='get_course_preview_list'),
   
    #students
    path('get-course-details/<str:course_public_id>/', views.get_course_details, name='get_course_details'),
    path('get-course-cards/', views.get_course_cards, name='get_course_cards'),
    path('get-course-cards-by-publisher-public-id/<str:publisher_public_id>/', views.get_course_cards_by_publisher_public_id, name='get_course_cards_by_publisher_public_id'),
    path('get-course-and-lessons/<str:course_public_id>/', views.get_course_and_lessons, name='get_course_and_lessons'),

]