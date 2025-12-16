from rest_framework import serializers
from .models import WithdrawBalanceRequest
from utils.validators import CommonValidators
from Constants import PAYMENT_WAYS_ARRAY

class WithdrawBalanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawBalanceRequest
        fields = [
            "id",
            "user_id",
            "full_name",
            "email",
            "phone",
            "wanted_amount",
            "original_balance",
            "order_date_time",
            "city",
            "confirmed",
            "confirmation_date_time",
            "payment_way",
            "shamcash_code",
        ]

class MakeWithdrawBalanceRequestParametersSerializer(serializers.Serializer):
    
    amount = serializers.FloatField( min_value=1) # amount of money to withdraw
    payment_way = serializers.ChoiceField( choices=PAYMENT_WAYS_ARRAY)
    shamcash_code = serializers.CharField(required=False , max_length=100) # shamcash code if payment way is shamcash
    # full_name = serializers.CharField(required=True , max_length=300)
    # phone = serializers.CharField(required=False , max_length=15)
    def validate_amount(self, value):
        return CommonValidators.validate_money_amount(value, "المبلغ")
    
    def validate_shamcash_code(self, value):
        if value is not None and value != "":
            return CommonValidators.validate_text_field(value, "رمز شام كاش", max_length=50)
        return value
 