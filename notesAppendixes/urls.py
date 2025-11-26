from django.urls import path

from .views import (
    create_note_appendix,
    get_note_appendix,
    update_note_appendix,
    delete_note_appendix,
)


urlpatterns = [
    path("create/", create_note_appendix, name="create_note_appendix"),
    path("<str:note_public_id>/", get_note_appendix, name="get_note_appendix"),
    path(
        "<str:note_public_id>/update/",
        update_note_appendix,
        name="update_note_appendix",
    ),
    path(
        "<str:note_public_id>/delete/",
        delete_note_appendix,
        name="delete_note_appendix",
    ),
]

