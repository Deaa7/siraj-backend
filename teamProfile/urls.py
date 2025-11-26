from django.urls import path
from . import views
    
urlpatterns = [
    path('change-number-of-exams/', views.change_number_of_exams, name='change-number-of-exams'),
    path('change-number-of-notes/', views.change_number_of_notes, name='change-number-of-notes'),
    path('change-number-of-courses/', views.change_number_of_courses, name='change-number-of-courses'),
    path('change-number-of-followers/', views.change_number_of_followers, name='change-number-of-followers'),
    path('update-profile/', views.update_team_profile, name='update-team-profile'),
    path('public-profile/<str:team_uuid>/', views.public_team_profile.as_view(), name='public-team-profile'),
    path('own-profile/', views.own_team_profile, name='own-team-profile'),
]
