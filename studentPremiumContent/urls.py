from django.urls import path

from . import views

urlpatterns = [
    path(
        "get-student-premium-content-cards/",
        views.get_student_premium_content_cards,
        name="get_student_premium_content_cards",
    ),
]