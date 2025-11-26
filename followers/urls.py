from django.urls import path

from . import views


urlpatterns = [
    path(
        'follow/<str:public_user_id>/',
        views.follow_user,
        name='follow_user',
    ),
    path(
        'unfollow/<str:public_user_id>/',
        views.unfollow_user,
        name='unfollow_user',
    ),
    path(
        'is-following/<str:public_user_id>/',
        views.is_following_user,
        name='is_following_user',
    ),
]

