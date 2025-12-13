from django.urls import path
from . import views

urlpatterns = [
    # List units (GET) - filtered by Class and subject_name, returns only name and slug
    path('get-units/', views.get_units, name='get_units'),
    
    # Get unit detail (GET)
    path('get-unit-detail/<str:unit_public_id>/', views.get_unit_detail, name='get_unit_detail'),
    
    # Create unit (POST)
    path('create/', views.create_unit, name='create_unit'),
    
    # Update unit (PUT/PATCH)
    path('update/<str:unit_public_id>/', views.update_unit, name='update_unit'),
    
    # Delete unit (DELETE)
    path('delete/<str:unit_public_id>/', views.delete_unit, name='delete_unit'),
]

