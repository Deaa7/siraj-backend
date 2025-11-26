from django.urls import path

from . import views


urlpatterns = [
    path("create-post/", views.create_post, name="create_post"),
    path("update-post/<str:post_public_id>/", views.update_post, name="update_post"),
    path("delete-post/<str:post_public_id>/", views.delete_post, name="delete_post"),
    path("get-posts-list/", views.get_posts_list, name="get_posts_list"),
    path("get-posts-by-publisher/<str:publisher_public_id>/", views.get_posts_by_publisher, name="get_posts_by_publisher"),
    path("change-number-of-comments/<str:post_public_id>/", views.change_number_of_comments, name="change_number_of_comments"),
    path("toggle-post-active/<str:post_public_id>/", views.toggle_post_active, name="toggle_post_active"),
]

