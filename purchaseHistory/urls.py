from django.urls import path
from . import views



urlpatterns = [
    path('publisher_number_of_purchases_and_profit_last_month/', views.publisher_number_of_purchases_and_profit_last_month, name='publisher_number_of_purchases_and_profit_last_month'),
    path('publisher_purchases_grouped_by_gender_and_city_last_month/', views.publisher_purchases_grouped_by_gender_and_city_last_month, name='publisher_purchases_grouped_by_gender_and_city_last_month'),
    path('content_purchase_history_dashboard_list/', views.content_purchase_history_dashboard_list, name='content_purchase_history_dashboard_list'),
]