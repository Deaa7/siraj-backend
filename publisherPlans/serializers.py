from rest_framework import serializers
from .models import PublisherPlans


class PublisherPlanSerializer(serializers.ModelSerializer):
  
  plan_name = serializers.CharField(source="offer.offer_name")
  number_of_allowed_exams = serializers.IntegerField(source="offer.number_of_exams")
  number_of_allowed_notes = serializers.IntegerField(source="offer.number_of_notes")
  number_of_allowed_courses = serializers.IntegerField(source="offer.number_of_courses")
  plan_price = serializers.IntegerField(source="offer.offer_price")
  class Meta:
        model = PublisherPlans
        fields = [
            "plan_name",
            "plan_price",
            "number_of_allowed_notes",
            "number_of_allowed_courses",
            "number_of_allowed_exams",
            "auto_renew",
            "plan_expiration_date",
            "activation_date",
        ]