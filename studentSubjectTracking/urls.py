from django.urls import path

from . import views

urlpatterns = [
    path(
        "get-student-subject-tracking/",
        views.get_student_subject_tracking,
        name="get-student-subject-tracking",
    ),
]
