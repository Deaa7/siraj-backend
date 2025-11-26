from django.urls import path
from . import views


urlpatterns = [
    path(
        'note-read-tracking-cards/<str:public_student_id>/',
        views.get_note_read_tracking_cards,
        name='get_note_read_tracking_cards',
    ),
    path(
        'create-note-read-tracking/<str:note_public_id>/',
        views.create_note_read_tracking,
        name='create_note_read_tracking',
    ),
    path('update-note-read_tracking-metrics/<str:note_public_id>/' , views.update_note_read_tracking_metrics , name= "update_note_read_tracking_metrics")
]

