from rest_framework import serializers
from .models import PublisherOffers

class PublisherOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublisherOffers
        fields = [
            "public_id",
            "offer_name",
            "offer_price",
            "offer_for",
            "number_of_exams",
            "number_of_notes",
            "number_of_courses",
        ]