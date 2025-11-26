from rest_framework import serializers

from chargingOrders.models import ChargingOrders


class ChargingOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating charging order information"""
    class Meta:
        model = ChargingOrders
        fields = [
            "payment_way",
            "payment_photo",
            "amount",
        ]
 
    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("المبلغ يجب أن يكون أكبر من 0")
        return value


class GetChargingOrdersSerializer(serializers.ModelSerializer):

   email = serializers.CharField(source="user.email", read_only=True)
   account_category = serializers.CharField(
        source="user.account_category", read_only=True
    )
   full_name = serializers.CharField(source="user.full_name", read_only=True)
   phone = serializers.CharField(source="user.phone", read_only=True)
   user_public_id = serializers.CharField(source="user.uuid", read_only=True)
   account_type = serializers.CharField(source="user.account_type", read_only=True)
  
   class Meta:
        model = ChargingOrders
        fields = [
            "public_id",
            "user_public_id",
            "full_name",
            "payment_way",
            "payment_photo",
            "amount",
            "status",
            "confirmation_date",
            "email",
            "phone",
            "account_type",
            "created_at",
        ]

        """
        for cusom logic  :
         
        def get_category_name(self, obj):
        # The category is already loaded via select_related, so no extra query
        if obj.user:
            return obj.user.email
        return None
    
        def get_phone(self, obj):
            if obj.user:
                return obj.user.phone
            return None
        """
