from django.urls import path
from . import views

urlpatterns = [
  path('get-withdraw-balance-requests/' , views.get_withdraw_balance_requests  , name = 'get-withdraw-balance-requests' ),
  path('confirm-withdraw-balance-request/<str:request_id>/' , views.confirm_withdraw_balance_request  , name = 'confirm-withdraw-balance-request' ),
  
  path('change-user-balance/<str:user_uuid>/', views.change_user_balance, name='change-user-balance'),

  path('block-content/<str:content_public_id>/', views.block_content, name='block-content'),
  path('unblock-content/<str:content_public_id>/', views.unblock_content, name='unblock-content'),
  
  path('get-charging-orders/', views.get_charging_orders, name='get-charging-orders'),
  path('validate-charging-order/<str:order_public_id>/', views.validate_charging_order, name='validate-charging-order'),
  path('cancel-charging-order/<str:order_public_id>/', views.cancel_charging_order, name='cancel-charging-order'),
  
  path('ban-user/<str:user_uuid>/', views.ban_user, name='ban-user'),
  path('unban-user/<str:user_uuid>/', views.unban_user, name='unban-user'),
  
]
 