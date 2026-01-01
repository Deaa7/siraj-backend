

from rest_framework.decorators import  permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import ChargingOrders

from .serializers import ChargingOrderCreateSerializer


class create_charging_order(APIView):

    permission_classes([IsAuthenticated])
    throttle_classes = [ScopedRateThrottle]
    # throttle_scope = "create_charging_order"  # Custom scope name

    def post(self, request):
        """
        Create a charging order
        """
        
        serializer = ChargingOrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            
            # check if we have previous charging order that is pending
            previous_charging_order = ChargingOrders.objects.filter(
                user=request.user, status="pending"
            ).first()
            
            if previous_charging_order:
                return Response(
                    {"message": "لديك طلب شحن رصيد سابق قيد المعالجة"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            serializer.save(user=request.user)
            
            return Response(
                {"message": "تم إنشاء الطلب بنجاح"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




"""
other endpoints of this file are in adminApp/views.py
"""