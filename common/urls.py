from django.urls import path
from . import views

urlpatterns = [
    path('disable-exam/<str:exam_public_id>/', views.disable_exam, name='disable-exam'),
    path('activate-exam/<str:exam_public_id>/', views.activate_exam, name='activate-exam'),
    
    path('disable-note/<str:note_public_id>/', views.disable_note, name='disable-note'),
    path('activate-note/<str:note_public_id>/', views.activate_note, name='activate-note'),
    
    path('disable-course/<str:course_public_id>/', views.disable_course, name='disable-course'),
    path('activate-course/<str:course_public_id>/', views.activate_course, name='activate-course'),
    
    path('purchase-content/', views.purchase_content, name='purchase-content'),
    path('publisher-most-popular-content-preview/', views.publisher_most_popular_content_preview, name='publisher-most-popular-content-preview'),
    path('publisher-most-purchased-content-preview/', views.publisher_most_purchased_content_preview, name='publisher-most-purchased-content-preview'),
    path('publisher-most-profitable-content-preview/', views.publisher_most_profitable_content_preview, name='publisher-most-profitable-content-preview'),


    path('publisher-student-analysis-last-month-date/', views.publisher_student_analysis_last_month_date, name='publisher_student_analysis_last_month_date'),
    path('publisher-student-analysis-last-month-city/', views.publisher_student_analysis_last_month_city, name='publisher_student_analysis_last_month_city'),
    path('publisher-student-analysis-last-month-gender/', views.publisher_student_analysis_last_month_gender, name='publisher_student_analysis_last_month_gender'),
    
    path('platform-statistics/', views.platform_statistics, name='platform-statistics'),
    path('publisher-statistics/', views.publisher_statistics, name='publisher-statistics'),
    path('check-publishing-availability/', views.check_publishing_availability, name='check-publishing-availability'),
   
     path('create-presigned-url/', views.PresignedURLView.as_view(), name='create-presigned-url'),
]