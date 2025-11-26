from django.urls import path
from . import views


urlpatterns = [
    path(
        'exam-app-tracking-cards/<str:public_student_id>/',
        views.get_exam_app_tracking_cards,
        name='get_exam_app_tracking_cards',
    ),
    path(
        'create-exam-app-tracking/<str:exam_public_id>/',
        views.create_exam_app_tracking,
        name='create_exam_app_tracking',
    ),
    path(
        'update-exam-app-tracking-metrics/<str:exam_public_id>/',
        views.update_exam_app_tracking_metrics,
        name='update_exam_app_tracking_metrics',
    ),
]

