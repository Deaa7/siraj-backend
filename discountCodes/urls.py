from django.urls import path
from . import views

urlpatterns = [
    # publishers
    path('create-discount-code/', views.create_discount_code, name='create_discount_code'),
    path('update-discount-code/<str:discount_code_public_id>/', views.update_discount_code, name='update_discount_code'),
    path('delete-discount-code/<str:discount_code_public_id>/', views.delete_discount_code, name='delete_discount_code'),
    path('get-discount-codes-list/', views.get_discount_codes_list, name='get_discount_codes_list'),
    path('get-discount-codes-list-by-content-public-id/<str:content_public_id>/', views.get_discount_codes_list_by_content_public_id, name='get_discount_codes_list_by_content_public_id'),
   
    # all
    path('validate-discount-code/', views.validate_discount_code, name='validate_discount_code'),
]

