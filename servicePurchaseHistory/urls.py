from django.urls import path

from . import views

urlpatterns = [
    path(
        "get-service-purchase-history/",
        views.get_service_purchase_history,
        name="get_service_purchase_history",
    ),
]

