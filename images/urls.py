from django.urls import path

from . import views


urlpatterns = [
    path(
        'posts/<str:post_public_id>/images/',
        views.get_images_by_post,
        name='get_images_by_post',
    ),
    path(
        'posts/<str:post_public_id>/images/add/',
        views.add_image,
        name='add_image',
    ),
    path(
        'images/<str:image_public_id>/delete/',
        views.delete_image,
        name='delete_image',
    ),
]


