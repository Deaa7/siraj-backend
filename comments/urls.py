from django.urls import path

from . import views

urlpatterns = [
    path("create-comment/", views.create_comment, name="create_comment"),
    path("update-comment/<str:comment_public_id>/", views.update_comment, name="update_comment"),
    path("delete-comment/<str:comment_public_id>/", views.delete_comment, name="delete_comment"),
    path("get-content-comments/<str:content_public_id>/", views.get_content_comments, name="get_content_comments"),
    path("get-content-comments-number/<str:content_public_id>/", views.get_content_comments_number, name="get_content_comments_number"),

]