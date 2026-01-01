from rest_framework import serializers
from .models import WithdrawBalanceRequest
from utils.validators import CommonValidators
from Constants import PAYMENT_WAYS_ARRAY , CITIES_ARRAY

class WithdrawBalanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawBalanceRequest
        fields = [
            "public_id",
            "user_id",
            "full_name",
            "email",
            "phone",
            "wanted_amount",
            "original_balance",
            "created_at",
            "city",
            "confirmed",
            "confirmation_date_time",
            "payment_way",
            "meta_data",
        ]

class MakeWithdrawBalanceRequestParametersSerializer(serializers.Serializer):
    
    amount = serializers.FloatField( min_value=1) # amount of money to withdraw
    payment_way = serializers.ChoiceField( choices=PAYMENT_WAYS_ARRAY)
    meta_data = serializers.CharField(required=False , max_length=200 , allow_blank=True , allow_null=True ) 
    full_name = serializers.CharField(required=True , max_length=300)
    phone = serializers.CharField(required=False , max_length=15)
    city = serializers.ChoiceField(choices=CITIES_ARRAY)
    
    def validate_amount(self, value):
        return CommonValidators.validate_money_amount(value, "المبلغ")
    
    def validate_meta_data(self, value):
        if not value : 
            return value 
        return CommonValidators.validate_text_field(value, "البيانات الإضافية", max_length=200 , allow_empty=True)
    
    def validate_full_name(self, value):
        if  not value :
            raise serializers.ValidationError("يجب أن يكون لديك اسم")
        
        return CommonValidators.validate_text_field(value, "الاسم", max_length=300)