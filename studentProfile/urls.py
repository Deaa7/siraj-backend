from django.urls import path
from . import views

urlpatterns = [

    path("update-student-profile/<int:user_id>/", views.update_student_profile, name="update_student_profile"),
    path("increase-number-of-completed-courses/<int:user_id>/",views.increase_number_of_completed_courses, name="increase_number_of_completed_courses"),
    path("increase-number-of-read-notes/<int:user_id>/",views.increase_number_of_read_notes, name="increase_number_of_read_notes"),
    path("increase-number-of-done-exams/<int:user_id>/",views.increase_number_of_done_exams, name="increase_number_of_done_exams"),
    path("public-student-profile/<int:student_id>/",views.public_student_profile.as_view(), name="public_student_profile"),
    path("own-student-profile/<int:user_id>/",views.own_student_profile, name="own_student_profile"),

]