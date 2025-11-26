from django.urls import path

from . import views

urlpatterns = [
    path(
        "mark-as-read/<str:notification_public_id>/",
        views.mark_notification_as_read,
        name="mark_notification_as_read",
    ),
    path(
        "list/<str:user_public_id>/",
        views.get_notifications_list,
        name="get_notifications_list",
    ),
    path(
        "delete/<str:notification_public_id>/",
        views.delete_notification,
        name="delete_notification",
    ),
]

