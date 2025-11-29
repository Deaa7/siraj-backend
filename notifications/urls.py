from django.urls import path

from . import views

urlpatterns = [
    path(
        "mark-as-read/<str:notification_public_id>/",
        views.mark_notification_as_read,
        name="mark_notification_as_read",
    ),
    path(
        "mark-all-notifications-as-read/",
        views.mark_all_notifications_as_read,
        name="mark_all_notifications_as_read",
    ),
    path(
        "get-notifications-list/",
        views.get_notifications_list,
        name="get_notifications_list",
    ),
    path(
        "delete/<str:notification_public_id>/",
        views.delete_notification,
        name="delete_notification",
    ),
    path(
        "delete-all-notifications/",
        views.delete_all_notifications,
        name="delete_all_notifications",
    ),
    path(
        "get-unread-notifications-count/",
        views.get_unread_notifications_count,
        name="get_unread_notifications_count",
    ),
]

