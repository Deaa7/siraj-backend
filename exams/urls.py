from django.urls import path
from . import views

urlpatterns = [
    
    path('change-exam-metrics/<str:exam_public_id>/', views.change_exam_metrics, name='change_exam_metrics'),
    path('increase-number-of-purchases/<str:exam_public_id>/', views.increase_number_of_purchases, name='increase_number_of_purchases'),
    
    #publishers
    path('create-exam/', views.create_exam, name='create_exam'),
    path('change-number-of-comments/<str:exam_public_id>/', views.change_number_of_comments, name='change_number_of_comments'),
    path('update-exam/<str:exam_public_id>/', views.update_exam, name='update_exam'),
    path('delete-exam/<str:exam_public_id>/', views.delete_exam, name='delete_exam'),
    path('get-exams-list-for-dashboard/', views.get_exams_list_for_dashboard, name='get_exams_list_for_dashboard'),
    path('get-average-results-for-all-exams-by-publisher-id/', views.get_average_results_for_all_exams_by_publisher_id, name='get_average_results_for_all_exams_by_teacher_id'),
    path('get-exam-details-for-dashboard/<str:exam_public_id>/', views.get_exam_details_for_dashboard, name='get_exam_details_for_dashboard'),
    path('get-exam-preview-list/', views.get_exam_preview_list, name='get_exam_preview_list'),
    
    #students
    path('get-exam-details/<str:exam_public_id>/', views.get_exam_details, name='get_exam_details'),
    path('get-exam-cards/', views.get_exam_cards, name='get_exam_cards'),
    path('get-exam-cards-by-publisher-public-id/<str:publisher_public_id>/', views.get_exam_cards_by_publisher_public_id, name='get_exam_cards_by_publisher_public_id'),
    path('get-exam-and-mcqs/<str:exam_public_id>/', views.get_exam_and_mcqs, name='get_exam_and_mcqs'),
]
