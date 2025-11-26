from rest_framework import serializers
from .models import WithdrawBalanceRequest
from utils.validators import CommonValidators


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
    
    amount = serializers.FloatField( min_value=0) # amount of money to withdraw
    payment_way = serializers.ChoiceField( choices=["shamcash", "bank"])
    shamcash_code = serializers.CharField(required=False , max_length=100) # shamcash code if payment way is shamcash
    full_name = serializers.CharField(required=True , max_length=300)
    phone = serializers.CharField(required=False , max_length=15)
    def validate_amount(self, value):
        return CommonValidators.validate_money_amount(value, "المبلغ")
    
    def validate_shamcash_code(self, value):
        if value is not None and value != "":
            return CommonValidators.validate_text_field(value, "رمز شام كاش", max_length=50)
        return value
    def validate_full_name(self, value):
        if value is None or value == "":
            raise serializers.ValidationError("الاسم الكامل مطلوب")
        if len(value) > 300:
            raise serializers.ValidationError("الاسم الكامل يجب أن يكون أقل من 300 حرف")
        return CommonValidators.validate_arabic_text(value, "الاسم الكامل", max_length=300)
    
    def validate_phone(self, value):
        if value is not None and value != "":
            return CommonValidators.validate_phone(value, "رقم الهاتف")
        return value