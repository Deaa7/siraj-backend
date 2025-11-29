from django.urls import path
from . import views



urlpatterns = [
    path('publisher-number-of-purchases-last-month/', views.publisher_number_of_purchases_last_month, name='publisher_number_of_purchases_last_month'),
    path('publisher-profit-last-month/', views.publisher_profit_last_month, name='publisher_profit_last_month'),
    path(
        "publisher-purchases-grouped-by-city-last-month/",
        views.publisher_purchases_grouped_by_city_last_month,
        name="publisher_purchases_grouped_by_city_last_month",
    ),
    path(
        "publisher-purchases-grouped-by-gender-last-month/",
        views.publisher_purchases_grouped_by_gender_last_month,
        name="publisher_purchases_grouped_by_gender_last_month",
    ),
    path('purchase-history-list/', views.purchase_history_list, name='purchase_history_list'),
]