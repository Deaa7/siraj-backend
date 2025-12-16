from django.shortcuts import  get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

#models 
from .models import WithdrawBalanceRequest
from users.models import User
from transactions.models import Transactions

#serializers
from .serializers import (
    MakeWithdrawBalanceRequestParametersSerializer,
)
 
class make_withdraw_balance_request(APIView):
    
  permission_classes = [IsAuthenticated]
  throttle_classes = [ScopedRateThrottle]
  throttle_scope = 'make_withdraw_balance_request'
  
  def post(self, request):
      
    user_id = request.user.id
     
    user = get_object_or_404(User, id=user_id)

    if user is None:
        return Response(
            {"error": "المستخدم غير موجود"}, status=status.HTTP_404_NOT_FOUND
        )
        
    if user.account_type == "student" :
        return Response(
            {"error": "لا يحق لك تقديم طلب سحب رصيد"}, status=status.HTTP_404_NOT_FOUND
        )
  
    serializer = MakeWithdrawBalanceRequestParametersSerializer(data=request.data)

    if serializer.is_valid():

        amount = serializer.validated_data.get("amount")
        payment_way = serializer.validated_data.get("payment_way")
        shamcash_code = serializer.validated_data.get("shamcash_code")

        WithdrawBalanceRequest.objects.create(
            user_id=user,
            wanted_amount=amount,
            payment_way=payment_way,
            full_name=user.full_name,   
            email=user.email,
            phone=user.phone,
            city=user.city,
            original_balance=user.balance,
            shamcash_code=shamcash_code,
        )
        
        Transactions.objects.create(
            user=user,
            full_name=user.full_name,
            amount=amount,
            transaction_type="withdraw",
            balance_before=user.balance,
            balance_after=user.balance - amount,
            transaction_status="pending",
        )
        
        user.balance -= amount
        user.save()

        return Response(
            {"message": "تم إرسال طلب سحب رصيد بنجاح"}, status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

