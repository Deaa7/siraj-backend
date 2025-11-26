from django.shortcuts import  get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from datetime import datetime
from dotenv import load_dotenv
import os
from django.utils import timezone
#models 
from withdrawBalanceRequest.models import WithdrawBalanceRequest
from users.models import User
from transactions.models import Transactions
from notifications.models import Notifications
from chargingOrders.models import ChargingOrders
from exams.models import Exam
from notes.models import Note
from courses.models import Course
from teacherProfile.models import TeacherProfile
from teamProfile.models import TeamProfile

#serializers
from withdrawBalanceRequest.serializers import  WithdrawBalanceRequestSerializer
from chargingOrders.serializers import GetChargingOrdersSerializer

# tasks 
from chargingOrders.tasks import charging_order_success_email_notification

load_dotenv()


"""
this file holds endpoints that only admin can access

"""


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def ban_user(request, user_uuid):
    """
    Ban a user
    """
    admin = request.user
    admin = get_object_or_404(User, id=request.user.id)
    if admin.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لحظر هذا الحساب"}, status=status.HTTP_403_FORBIDDEN)
    
    user = get_object_or_404(User, uidd=user_uuid)
    user.is_banned = True
    user.banning_reason = request.data.get("reason")
    user.banning_date = timezone.now()
    user.save()
    return Response({"message": "تم حظر الحساب بنجاح"}, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def unban_user(request, user_uuid):
    """
    Unban a user
    """
    admin = request.user
    admin = get_object_or_404(User, id=request.user.id)
    if admin.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لإلغاء حظر هذا الحساب"}, status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(User, uidd=user_uuid)
    user.is_banned = False
    user.banning_date = None
    user.save()
    return Response({"message": "تم إلغاء حظر الحساب بنجاح"}, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(["POST"])
def  block_content(request , content_public_id):
   """
    Block content
   """
   try:
    admin = request.user
    admin = get_object_or_404(User, id=request.user.id)
   
    if admin.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لحظر هذا المحتوى"}, status=status.HTTP_403_FORBIDDEN)
    
    content_type = request.data.get("content_type")
    content = None 
    if content_type == "exam" : 
        content = get_object_or_404(Exam, public_id=content_public_id)
    elif content_type == "note" : 
        content = get_object_or_404(Note, public_id=content_public_id)
    elif content_type == "course" : 
        content = get_object_or_404(Course, public_id=content_public_id)
    
    content.active = False 
    content.disabled_by = "admin" 
    content.disabled_at = timezone.now()
    
    publisher = User.objects.get(id=content.publisher_id)
   
    if publisher.account_type == "teacher":
        publisher = TeacherProfile.objects.get(id=publisher.id)
    elif publisher.account_type == "team":
        publisher = TeamProfile.objects.get(id=publisher.id)
    
    if content_type == "exam":
        publisher.number_of_exams -= 1
    elif content_type == "note":
        publisher.number_of_notes -= 1
    elif content_type == "course":
        publisher.number_of_courses -= 1
    
    publisher.save()
    content.save()
    return Response({"message": "تم حظر المحتوى بنجاح"}, status=status.HTTP_200_OK)
   
   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def unblock_content(request , content_public_id):
    """
    Unblock content
    """
    try:
        admin = request.user
        admin = get_object_or_404(User, id=request.user.id)
        
        if admin.account_type != "admin":
            return Response(
                {"error": "لا تملك صلاحية لإلغاء حظر هذا المحتوى"}, status=status.HTTP_403_FORBIDDEN)
        
        content_type = request.data.get("content_type")
        content = None 
        if content_type == "exam" : 
            content = get_object_or_404(Exam, public_id=content_public_id)
        elif content_type == "note" : 
            content = get_object_or_404(Note, public_id=content_public_id)
        elif content_type == "course" : 
            content = get_object_or_404(Course, public_id=content_public_id)
        
        content.active = True 
        content.disabled_at = None 
        content.save()
        
        publisher = User.objects.get(id=content.publisher_id)
        if publisher.account_type == "teacher":
            publisher = TeacherProfile.objects.get(id=publisher.id)
        elif publisher.account_type == "team":
            publisher = TeamProfile.objects.get(id=publisher.id)
        
        if content_type == "exam":
            publisher.number_of_exams += 1
        elif content_type == "note":
            publisher.number_of_notes += 1
        elif content_type == "course":
            publisher.number_of_courses += 1
        publisher.save()
        content.save()
        return Response({"message": "تم إلغاء حظر المحتوى بنجاح"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_withdraw_balance_requests(request):

    user_id = request.user.id
    user = User.objects.get(id = user_id)

    limit = request.data.get("limit", 10)
    count = request.data.get("count", 0)
    limit = int(limit)
    count = int(count)
  
    if user.role != "admin":
        return Response(
            {"error": "لا تملك صلاحية لعرض هذا الطلب"}, status=status.HTTP_403_FORBIDDEN
        )

    withdraw_balance_request = WithdrawBalanceRequest.objects.filter(confirmed=False)

    begin = count * limit
    end = (count + 1) * limit
    
    if end > len(serializer.data):
        end = len(serializer.data)

    if begin > len(serializer.data):
        begin = len(serializer.data)
    
    serializer = WithdrawBalanceRequestSerializer(withdraw_balance_request[begin : end], many=True)

    data = serializer.data

    return Response(
        {"withdraw_request": data, "total_number": len(serializer.data)}, status=status.HTTP_200_OK
    )


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def confirm_withdraw_balance_request(request, request_id):

    user_id = request.user.id
    user = User.objects.get(id = user_id)
    if user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لتأكيد هذا الطلب"},
            status=status.HTTP_403_FORBIDDEN,
        )

    withdraw_balance_request = get_object_or_404(WithdrawBalanceRequest, id=request_id)
    withdraw_balance_request.confirmed = True
    withdraw_balance_request.confirmation_date_time = datetime.now()
    withdraw_balance_request.save()
    
    transaction = Transactions.objects.filter(user_id=user.id, transaction_type="withdraw" , transaction_status="pending").first()
   
    if transaction is None:
        return Response({"error": "لا يوجد سجل لهذه المعاملة"}, status=status.HTTP_404_NOT_FOUND)
    
    transaction.transaction_status = "completed"
    transaction.save()
    return Response({"message": "تم تأكيد الطلب بنجاح"}, status=status.HTTP_200_OK)

 
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def change_user_balance(request, user_uuid):  # increasing bonus

    user = request.user
    
    if user.account_type != "admin":
        return Response(
            {"error": "ليس لديك صلاحية لهذا الإجراء"},
            status=status.HTTP_403_FORBIDDEN,
        )
        
    user_public_id = user_uuid
    amount = request.data["amount"]
    
    user = get_object_or_404(User, uuid=user_public_id)
    
    if user.is_deleted:
        return Response(
            {"error": "الحساب غير موجود"},
            status=status.HTTP_404_NOT_FOUND,
        )
    
    if user.is_banned:
        return Response(
            {"error": "تم حظر الحساب. السبب: " + (user.banning_reason or "غير محدد")},
            status=status.HTTP_403_FORBIDDEN,
        )
    
    owner_id = os.getenv("OWNER_ID")
    owner = User.objects.get(id=owner_id)    
    
    if owner.balance < amount:
        return Response(
            {"error": "الرصيد المتاح للمنصة غير كافي"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    if amount > 0:
        
        # increase user balance and decrease owner balance
                
        Transactions.objects.create(
        user_id=user,
        full_name=user.full_name,
        amount=amount,
        transaction_type="bonus",
        balance_before=user.balance,
        balance_after=user.balance + amount,
        transaction_status="success",
        )
        
        user.balance += amount
        user.save()

        Transactions.objects.create(
        user_id=owner,
        full_name="منصة سراج التعليمية",
        amount=amount,
        transaction_type="bonus",
        balance_before=user.balance,
        balance_after=user.balance + amount,
        transaction_status="success",
         )
        owner.balance -= amount
        owner.save()
        
        

        Notifications.objects.create(
        receiver_id=user,
        source_type="siraj-management",
        title="مكافأة مالية",
        content=f"تم إضافة مكافأة مالية بمبلغ {amount} إلى حسابك",
        )
    
    else:
        # decrease user balance and increase owner balance
        Transactions.objects.create(
        user_id=user,
        full_name=user.full_name,
        amount=amount,
        transaction_type="penalty",
        balance_before=user.balance,
        balance_after=user.balance + amount,
        transaction_status="success",
    )
        
        user.balance += amount
        user.save()
        

        Transactions.objects.create(
        user_id=owner,
        full_name="منصة سراج التعليمية",
        amount=amount,
        transaction_type="penalty",
        balance_before=user.balance,
        balance_after=user.balance + amount,
        transaction_status="success",
    )
        owner.balance -= amount
        owner.save()
       
        Notifications.objects.create(
        receiver_id=user,
        source_type="siraj-management",
        title="خصم مالي",
        content=f"تم خصم مبلغ {amount} من حسابك",
        )

    return Response({"message": "تم تغيير الرصيد بنجاح"}, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_charging_orders(request):
    """
    Get all charging orders
    """

    limit = request.data.get("limit", 10)
    count = request.data.get("count", 0)
    
    charging_orders = ChargingOrders.objects.select_related("user").filter(status="pending")

    count = int(count)
    limit = int(limit)

    begin = count * limit
    end = (count + 1) * limit
    
    serializer = GetChargingOrdersSerializer(charging_orders[begin:end], many=True)

    return Response(
        {"message": "تم إحضار الطلبات بنجاح", "charging_orders": serializer.data, "total_number": len(serializer.data)},
        status=status.HTTP_200_OK,
    )


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def validate_charging_order(request, order_public_id):
    """
    Validate a charging order
    """
    
    user = request.user
    user = get_object_or_404(User, id=user.id)

    if user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لتأكيد هذا الطلب"},
            status=status.HTTP_403_FORBIDDEN,
        )

    charging_order = get_object_or_404(ChargingOrders, public_id=order_public_id)

    if charging_order.status == "pending":

        charging_order.status = "confirmed"
        charging_order.confirmation_date = timezone.now()

        amount = charging_order.amount
        user = charging_order.user

        charging_order.save()

        transaction =Transactions.objects.create(
            user=user,
            amount=amount,
            full_name=charging_order.full_name,
            transaction_type="charging",
            transaction_status="completed",
            balance_before=user.balance,
            balance_after=user.balance + amount,
        )
        
        user.balance += amount
        user.save()
        
        charging_order_success_email_notification.delay(user.email , user.full_name , amount , transaction.public_id )
        
        return Response({"message": "تم تأكيد الطلب بنجاح"}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": "حدث خطأ أثناء تأكيد الطلب"}, status=status.HTTP_400_BAD_REQUEST
        )


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def cancel_charging_order(request, order_id):
    """
    Cancel a charging order
    """
    user = request.user
    user = get_object_or_404(User, id=user.id)

    if user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لتأكيد هذا الطلب"},
            status=status.HTTP_403_FORBIDDEN,
        )
    reason = request.data.get("reason")

    charging_order = get_object_or_404(ChargingOrders, id=order_id)
    
    if charging_order.status != "pending":
        return Response(
            {"message": "الطلب قد تم معالجته من قبل"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        charging_order.status = "cancelled"
        charging_order.save()

        Notifications.objects.create(
            receiver_id=charging_order.user,
            source_type="charging_order",
            title=f"إلغاء طلب شحن الرصيد",
            content=reason,
            date_time=timezone.now(),
        )

        return Response({"message": "تم إلغاء الطلب بنجاح"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"message": f"حدث خطأ أثناء إلغاء الطلب: {e}"},
            status=status.HTTP_400_BAD_REQUEST,
        )



