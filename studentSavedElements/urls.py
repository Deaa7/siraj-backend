from django.urls import path

from . import views

urlpatterns = [
    path(
        "add-saved-element/",
        views.add_saved_element,
        name="add_saved_element",
    ),
    path(
        "delete-saved-element/<str:saved_element_public_id>/",
        views.delete_saved_element,
        name="delete_saved_element",
    ),
    path(
        "get-saved-elements-cards/",
        views.get_saved_elements_cards,
        name="get_saved_elements_cards",
    ),
]

