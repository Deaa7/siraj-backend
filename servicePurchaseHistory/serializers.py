from rest_framework import serializers

from .models import ServicePurchaseHistory


class ServicePurchaseHistorySerializer(serializers.ModelSerializer):
    user_public_id = serializers.CharField(source='user_id.uuid')

    class Meta:
        model = ServicePurchaseHistory
        fields = [
            "public_id",
            "full_name",
            "user_public_id",
            "user_type",
            "phone",
            "city",
            "service_name",
            "service_price",
            "purchase_date",
        ]

 

