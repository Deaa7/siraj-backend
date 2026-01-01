from django.urls import path
from . import views

urlpatterns = [
    path('teacher-register/', views.teacher_register, name='teacher-register'),
    path('team-register/', views.team_register, name='team-register'),
    path('student-register/', views.student_register, name='student-register'),
    path('login/', views.login, name='login'),
    path('publisher-login/', views.publisher_login, name='publisher-login'),
    path('admin-login/', views.admin_login, name='admin-login'),
    path('logout/', views.logout, name='logout'),
    path('refresh-token/', views.refresh_token, name='refresh-token'),
    path('generate-reset-password-otp/', views.generate_reset_password_otp, name='generate-reset-password-otp'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password-reset-confirm'),
    path('verify-account/', views.verify_account.as_view(), name='verify-account'),
    path('delete-account/', views.delete_account, name='delete-account'),
    path('check-reset-password-otp/' , views.check_reset_password_otp , name = "check-reset-password-otp")
]
