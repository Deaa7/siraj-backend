from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import dotenv
import os

#models
from .models import PublisherOffers
from users.models import User
from publisherPlans.models import PublisherPlans
from servicePurchaseHistory.models import ServicePurchaseHistory
from transactions.models import Transactions


dotenv.load_dotenv()


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def purchase_offer(request ,offer_public_id):
    
    publisher = request.user
    
    auto_renew = request.data.get("auto_renew", False)
    
    publisher = get_object_or_404(User, uuid=publisher.uuid)
    
    if publisher.account_type != "teacher" and publisher.account_type != "team":
        return Response({"error": "غير مصرح لك بشراء الباقة"}, status=status.HTTP_400_BAD_REQUEST)
    
    offer = get_object_or_404(PublisherOffers, uuid=offer_public_id)
    
    if publisher.balance < offer.offer_price:
        return Response({"error": "لا يوجد لديك رصيد كافي"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not offer.active:
        return Response({"error": "الباقة لم تعد متوفرة"}, status=status.HTTP_400_BAD_REQUEST)
    
    
    old_plan = PublisherPlans.objects.get(user=publisher)
    old_plan.offer = offer
    old_plan.auto_renew = auto_renew
    old_plan.plan_expiration_date = datetime.now() + timedelta(days=30)
    old_plan.activation_date = datetime.now()
    old_plan.save()
    
    _edit_balance_and_record_plan_purchase(publisher.id, offer.id)
    
    return Response(status=status.HTTP_200_OK)


def _edit_balance_and_record_plan_purchase(user_id , offer_id):
    
    user = get_object_or_404(User, id=user_id)
    offer = get_object_or_404(PublisherOffers, id=offer_id)
    
    # record the purchase in the service purchase history 
    ServicePurchaseHistory.objects.create(
        user_id=user.id,
        full_name=user.full_name,
        user_type=user.account_type,
        phone=user.phone,
        city=user.city,
        service_name=offer.offer_name,
        service_price=offer.offer_price,
        purchase_date=datetime.now(),
    )
    
   # increase owner balance by offer_price and record the purchase in  Transaction table for both user and owner
    owner = get_object_or_404(User, id=os.getenv("OWNER_ID"))
   
   # record the purchase in the transactions table for the user
    Transactions.objects.create(
    user=user,
    full_name=user.full_name,
    transaction_type="purchase",
    transaction_status="completed",
    amount=offer.offer_price,
    balance_before=user.balance,
    balance_after=user.blanace - offer.offer_price,
   )
    
    # record the purchase in the transactions table for the owner
    Transactions.objects.create(
    user=owner,
    full_name="منصة سراج التعليمية",
    transaction_type="purchase",
    transaction_status="completed",
    amount=offer.offer_price,
    balance_before=owner.balance,
    balance_after=owner.balance + offer.offer_price,
   )
    
    owner.balance += offer.offer_price
    owner.save()
    
    user.balance -= offer.offer_price
    user.save()
    
    