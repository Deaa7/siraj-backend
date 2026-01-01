from django.urls import path
from . import views

urlpatterns = [
  path('get-withdraw-balance-requests/' , views.get_withdraw_balance_requests  , name = 'get-withdraw-balance-requests' ),
  path('confirm-withdraw-balance-request/<str:request_public_id>/' , views.confirm_withdraw_balance_request  , name = 'confirm-withdraw-balance-request' ),
  path('reject-withdraw-balance-request/<str:request_public_id>/' , views.reject_withdraw_balance_request  , name = 'reject-withdraw-balance-request' ),
  path('change-user-balance/<str:user_uuid>/', views.change_user_balance, name='change-user-balance'),

  path('block-content/<str:content_public_id>/', views.block_content, name='block-content'),
  path('unblock-content/<str:content_public_id>/', views.unblock_content, name='unblock-content'),
  
  path('get-charging-orders/', views.get_charging_orders, name='get-charging-orders'),
  path('validate-charging-order/<str:order_public_id>/', views.validate_charging_order, name='validate-charging-order'),
  path('cancel-charging-order/<str:order_public_id>/', views.cancel_charging_order, name='cancel-charging-order'),
  
  path('block-user/<str:user_uuid>/', views.block_user, name='block-user'),
  path('unblock-user/<str:user_uuid>/', views.unblock_user, name='unblock-user'),
  
  path('get-platform-balance/', views.get_platform_balance, name='get-platform-balance'),
  path('get-platform-profits-analysis-last-month/', views.get_platform_profits_analysis_last_month, name='get-platform-profits-analysis-last-month'),

  path('get-service-purchases-list/', views.get_service_purchases_list, name='get-service-purchases-list'),
  path('get-content-purchases-list/', views.get_content_purchases_list, name='get-content-purchases-list'),
]
 