from django.urls import path

from . import views

urlpatterns = [
    path("get-report-list/", views.get_report_list, name="get_report_list"),
    path(
        "mark-report-as-verified/<str:report_public_id>/",
        views.mark_report_as_verified,
        name="mark_report_as_verified",
    ),
]

