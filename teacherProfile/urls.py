from django.urls import path
from . import views
    
urlpatterns = [
    # path('resend-otp/', views.resendOTP, name='resend-otp'),
    path('change-number-of-exams/', views.change_number_of_exams, name='change-number-of-exams'),
    path('change-number-of-notes/', views.change_number_of_notes, name='change-number-of-notes'),
    path('change-number-of-courses/', views.change_number_of_courses, name='change-number-of-courses'),
    path('change-number-of-followers/', views.change_number_of_followers, name='change-number-of-followers'),
    path('update-profile/', views.update_teacher_profile, name='update-teacher-profile'),
    path('public-profile/<str:public_id>/', views.public_teacher_profile.as_view(), name='public-teacher-profile'),
    path('own-teacher-profile/', views.own_teacher_profile, name='own-teacher-profile'),
    path('get-teacher-preview-cards/', views.get_teacher_preview_cards, name='get-teacher-preview-cards'),
]
