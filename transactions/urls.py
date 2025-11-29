from django.urls import path
from . import views


urlpatterns = [
    path('history-preview-of-publisher/', views.get_transactions_history_preview_of_publisher, name='get_transactions_history_preview_of_publisher'),
    path('history-of-publisher/', views.get_transactions_history_of_publisher, name='get_transactions_history_of_publisher'),
]