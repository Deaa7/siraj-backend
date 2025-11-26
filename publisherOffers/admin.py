from django.contrib import admin
from .models import PublisherOffers
# Register your models here.
@admin.register(PublisherOffers)
class PublisherOffersAdmin(admin.ModelAdmin):
    list_display = ['offer_name', 'offer_price', 'offer_for', 'number_of_exams', 'number_of_notes', 'number_of_courses', 'active']