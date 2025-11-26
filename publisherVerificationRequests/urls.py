from django.urls import path

from . import views

urlpatterns = [
    path(
        "get-publisher-verification-requests/",
        views.get_publisher_verification_requests,
        name="get_publisher_verification_requests",
    ),
    path(
        "approve-verification-request/<str:request_public_id>/",
        views.approve_verification_request,
        name="approve_verification_request",
    ),
    path(
        "reject-verification-request/<str:request_public_id>/",
        views.reject_verification_request,
        name="reject_verification_request",
    ),
]

