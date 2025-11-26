from django.urls import path
from . import views

urlpatterns = [
  path('make-withdraw-balance-request/' , views.make_withdraw_balance_request.as_view()  , name = 'make-withdraw-balance-request' ),
]
 