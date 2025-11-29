from django.urls import path
from . import views


urlpatterns = [
    #publishers
    path('create-note/', views.create_note, name='create_note'),
    path('increase-number-of-downloads/<str:note_public_id>/', views.increase_number_of_downloads, name='increase_number_of_downloads'),
    path('increase-number-of-purchases/<str:note_public_id>/', views.increase_number_of_purchases, name='increase_number_of_purchases'),
    # path('increase-number-of-reads/<str:note_public_id>/', views.increase_number_of_reads, name='increase_number_of_reads'),
    path('change-number-of-comments/<str:note_public_id>/', views.change_number_of_comments, name='change_number_of_comments'),
    path('update-note/<str:note_public_id>/', views.update_note, name='update_note'),
    path('delete-note/<str:note_public_id>/', views.delete_note, name='delete_note'),
    path('get-notes-list-for-dashboard/', views.get_notes_list_for_dashboard, name='get_notes_list_for_dashboard'),
    path('get-note-details-for-dashboard/<str:note_public_id>/', views.get_note_details_for_dashboard, name='get_note_details_for_dashboard'),
    path('get-note-preview-list/', views.get_note_preview_list, name='get_note_preview_list'),

 
    #student 
    path('get-note-details/<str:note_public_id>/', views.get_note_details, name='get_note_details'),
    path('get-note-cards/', views.get_note_cards, name='get_note_cards'),
    path('get-note-cards-by-publisher-public-id/<str:publisher_public_id>/', views.get_note_cards_by_publisher_public_id, name='get_note_cards_by_publisher_public_id'),
    path('get-note-content/<str:note_public_id>/', views.get_note_content, name='get_note_content'),
]
