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
from datetime import datetime, timedelta, date
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate

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
from purchaseHistory.models import PurchaseHistory
from servicePurchaseHistory.models import ServicePurchaseHistory

#serializers
from withdrawBalanceRequest.serializers import  WithdrawBalanceRequestSerializer
from chargingOrders.serializers import GetChargingOrdersSerializer
from servicePurchaseHistory.serializers import ServicePurchaseHistorySerializer
from purchaseHistory.serializers import AdminPurchaseHistorySerializer

load_dotenv()


"""
this file holds endpoints that only admin can access

"""



@permission_classes([IsAuthenticated])
@api_view(["POST"])
def block_user(request, user_uuid):
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
def unblock_user(request, user_uuid):
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
    if not user or user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لعرض هذا الطلب"}, status=status.HTTP_403_FORBIDDEN
        )

    limit = request.query_params.get("limit", 10)
    count = request.query_params.get("count", 0)
 
    limit = int(limit)
    count = int(count)
  

    withdraw_balance_request = WithdrawBalanceRequest.objects.filter(confirmed=False).order_by('-created_at')

    begin = count * limit
    end = (count + 1) * limit
    length = len(withdraw_balance_request)
    if end > length:
        end = length

    if begin > length:
        begin = length
 
    serializer = WithdrawBalanceRequestSerializer(withdraw_balance_request[begin : end], many=True)

    data = serializer.data

    return Response(
        {"withdraw_request": data, "total_number": length}, status=status.HTTP_200_OK
    )

@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def confirm_withdraw_balance_request(request, request_public_id):

    user_id = request.user.id
    user = User.objects.get(id = user_id)
    if user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لتأكيد هذا الطلب"},
            status=status.HTTP_403_FORBIDDEN,
        )

    withdraw_balance_request = get_object_or_404(WithdrawBalanceRequest, public_id=request_public_id)
    withdraw_balance_request.confirmed = True
    withdraw_balance_request.confirmation_date_time = datetime.now()
    
    transaction = Transactions.objects.filter(user_id=withdraw_balance_request.user_id, transaction_type="withdraw" , transaction_status="pending").first()
   
    if transaction is None:
        return Response({"error": "لا يوجد سجل لهذه المعاملة"}, status=status.HTTP_404_NOT_FOUND)
    
    transaction.transaction_status = "completed"
    withdraw_balance_request.save()
    transaction.save()
    payment_arabic_way = ""
    if withdraw_balance_request.payment_way == "shamcash": 
        payment_arabic_way = "محفظة شام كاش"
    if withdraw_balance_request.payment_way == "syriatel": 
        payment_arabic_way = "سيرياتيل كاش"      
    if withdraw_balance_request.payment_way == "fauad": 
        payment_arabic_way = "الفؤاد"  
    if withdraw_balance_request.payment_way == "haram": 
     payment_arabic_way = "الهرم"         
    Notifications.objects.create(
        receiver_id=withdraw_balance_request.user_id,
        source_type="management",
        source_id = "0",
        title="طلب سحب رصيد",
        content=f"تم إتمام طلب سحب الرصيد الخاص بك وتحويل مبلغ {int(withdraw_balance_request.wanted_amount):,} ل.س باستخدام {payment_arabic_way}"
    )
    
    # withdraw_balance_request_notification.delay(withdraw_balance_request.user_id.id, withdraw_balance_request.wanted_amount, withdraw_balance_request.payment_way)
    return Response({"message": "تم تأكيد الطلب بنجاح"}, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def reject_withdraw_balance_request(request, request_public_id):

    user_id = request.user.id
    reason = request.data.get("reason")
    user = User.objects.get(id = user_id)
 
    if not user or user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لعرض هذا الطلب"}, status=status.HTTP_403_FORBIDDEN
        )

    withdraw_balance_request = get_object_or_404(WithdrawBalanceRequest, public_id=request_public_id)
 
    
    transaction = Transactions.objects.filter(user_id=withdraw_balance_request.user_id, transaction_type="withdraw" , transaction_status="pending" , amount = withdraw_balance_request.wanted_amount).first()
   
    if transaction is None:
        return Response({"error": "لا يوجد سجل لهذه المعاملة"}, status=status.HTTP_404_NOT_FOUND)
    
    user = User.objects.get(id=withdraw_balance_request.user_id.id)
    user.balance += withdraw_balance_request.wanted_amount
    user.save()
    
    # delete the transaction history of the user balance 
    
    
    withdraw_balance_request.delete()
    transaction.delete()
       
    Notifications.objects.create(
        receiver_id=withdraw_balance_request.user_id,
        source_type="management",
        source_id = "0",
        title="رفض طلب سحب رصيد",
        content=reason
    )
    
    # withdraw_balance_request_notification.delay(withdraw_balance_request.user_id.id, withdraw_balance_request.wanted_amount, withdraw_balance_request.payment_way)
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
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    if not user or user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لعرض هذا الطلب"}, status=status.HTTP_403_FORBIDDEN
        )
    
    limit = request.query_params.get("limit", 10)
    count = request.query_params.get("count", 0)
    
    charging_orders = ChargingOrders.objects.select_related("user").filter(status="pending").order_by('-created_at')

    count = int(count)
    limit = int(limit)

    begin = count * limit
    end = (count + 1) * limit
    
    serializer = GetChargingOrdersSerializer(charging_orders[begin:end], many=True)

    return Response(
        {"charging_orders": serializer.data, "total_number": len(serializer.data)},
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

    if not user or user.account_type != "admin":
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

        Transactions.objects.create(
            user=user,
            amount=amount,
            full_name=user.full_name,
            transaction_type="charging",
            transaction_status="completed",
            balance_before=user.balance,
            balance_after=user.balance + amount,
        )
        
        
        user.balance += amount
        user.save()
        
        Notifications.objects.create(
        receiver_id=charging_order.user,
        source_type="management",
        source_id = "0",
        title="تأكيد طلب شحن الرصيد",
        content=f"تم شحن رصيدك بمبلغ {int(amount):,} ل.س بنجاح"
    )
    
        # charging_order_success_email_notification.delay(user.email , user.full_name , amount , transaction.public_id )
        
        return Response({"message": "تم تأكيد الطلب بنجاح"}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": "حدث خطأ أثناء تأكيد الطلب"}, status=status.HTTP_400_BAD_REQUEST
        )

@permission_classes([IsAuthenticated])
@api_view(["POST"])
def cancel_charging_order(request, order_public_id):
    """
    Cancel a charging order
    """
    user = request.user
    user = get_object_or_404(User, id=user.id)

    if not user or user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لإلغاء هذا الطلب"},
            status=status.HTTP_403_FORBIDDEN,
        )
    reason = request.data.get("reason")

    charging_order = get_object_or_404(ChargingOrders, public_id=order_public_id)
    
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
            source_type="management",
            source_id = "0",
            title="إلغاء طلب شحن الرصيد",
            content=reason,
        )

        return Response({"message": "تم إلغاء الطلب بنجاح"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"message": f"حدث خطأ أثناء إلغاء الطلب: {e}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_platform_balance(request) : 
    
    user = request.user
    user = get_object_or_404(User, id=user.id)
    
    if not user or user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لعرض الرصيد المتاح للمنصة"}, status=status.HTTP_403_FORBIDDEN
        )
        
    owner_id = os.getenv("OWNER_ID")
    owner = User.objects.get(id=owner_id)
    return Response({"balance": owner.balance}, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_platform_profits_analysis_last_month(request):
  
   user = request.user 
   user = get_object_or_404(User, id = user.id)
   if not user or user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لعرض الأرباح الشهرية للمنصة"}, status=status.HTTP_403_FORBIDDEN
        )
  
   try:
    current_time = timezone.now()
    start_date = current_time - timedelta(days=30)
   
    # Generate all dates in the range [current_date - 30 days, current_date]
    current_date = timezone.localtime(current_time).date()
    start_date_only = start_date.date() if isinstance(start_date, datetime) else start_date
    
    # Initialize date_stats with all dates in the range, set to 0
    date_stats = {}
    for i in range(31):  # 30 days + current day = 31 days
        date_key = (start_date_only + timedelta(days=i)).isoformat()
        date_stats[date_key] = {
            "date": date_key,
            "number_of_purchases": 0,
            "profit" : 0,
        }
    
         # Get actual purchase data
    daily_summary = (
            PurchaseHistory.objects.filter(
                purchase_date__gte=start_date,
            )
            .annotate(date_truncated=TruncDate("purchase_date"))
            .values("date_truncated")
            .annotate(
                number_of_purchases=Count("id"),
                profit=Sum("owner_profit"),
            )
        )
    
            # Update date_stats with actual data
    for entry in daily_summary:
            purchase_date = entry["date_truncated"]
            if purchase_date is None:
                continue

            date_key = purchase_date.isoformat()
            if date_key in date_stats:
                date_stats[date_key]["number_of_purchases"] = entry["number_of_purchases"]
                date_stats[date_key]["profit"] = entry["profit"]

    # Convert to list and sort by date (newest first)
    results = sorted(
        date_stats.values(), key=lambda item: item["date"] 
    )

    return Response({"platform_profits_last_month": results}, status=status.HTTP_200_OK)
   except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_service_purchases_list(request):
    user = request.user
    user = get_object_or_404(User, id=user.id)
    if not user or user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لعرض قائمة الشراء الخاص بالخدمات"}, status=status.HTTP_403_FORBIDDEN
        )
    limit = request.query_params.get("limit", 10)
    count = request.query_params.get("count", 0)
    limit = int(limit)
    count = int(count)
    service_purchases = ServicePurchaseHistory.objects.all().order_by('-created_at')
    total_number = service_purchases.count()
    begin = count * limit
    end = (count + 1) * limit
    if begin > total_number:
        begin = total_number 
    if end > total_number:
        end = total_number
 
    serializer = ServicePurchaseHistorySerializer(service_purchases[begin:end], many=True)
    return Response({"service_purchases": serializer.data, "total_number": total_number}, status=status.HTTP_200_OK)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_content_purchases_list(request):
    
    """
    Return paginated content purchases list.
    """
    user = request.user
    user = get_object_or_404(User, id=user.id)
    if not user or user.account_type != "admin":
        return Response(
            {"error": "لا تملك صلاحية لعرض قائمة الشراء الخاص بالخدمات"}, status=status.HTTP_403_FORBIDDEN
        )    
    try:
        limit = request.query_params.get("limit", 10)
        count = request.query_params.get("count", 0)
        limit = int(limit)
        count = int(count)
        content_purchases = PurchaseHistory.objects.all().order_by('-created_at')
        total_number = content_purchases.count()

        begin = count * limit
        end = (count + 1) * limit

        if begin > total_number:
            begin = total_number
        if end > total_number:
            end = total_number

        serializer = AdminPurchaseHistorySerializer(
            content_purchases[begin:end], many=True
        )
 

        return Response(
            {
                "history": serializer.data,
                "total_number": total_number,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)



