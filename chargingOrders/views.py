from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import  permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ChargingOrders
from .serializers import ChargingOrderCreateSerializer, GetChargingOrdersSerializer
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from services.parameters_validator import validate_pagination_parameters
from transactions.models import Transactions
from notifications.models import Notifications
from .tasks import charging_order_success_email_notification


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
                
            serializer.save(user=request.user , partial=True)
            
            return Response(
                {"message": "تم إنشاء الطلب بنجاح"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




"""
other endpoints of this file are in adminApp/views.py
"""