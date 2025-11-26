from rest_framework import serializers
from .models import Transactions

class TransactionsSerializer(serializers.ModelSerializer):
 
    type = serializers.SerializerMethodField( method_name='get_type')
    class Meta:
        model = Transactions
        fields = [
            'amount',
            'created_at',
            'type',
            'transaction_type',
        ]
    
    def get_type(self, obj):
    
     if obj.balance_before > obj.balance_after:
        return 'decrease'
     elif obj.balance_before < obj.balance_after:
        return 'increase'
     else:
        return 'no change'