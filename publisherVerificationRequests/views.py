from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notifications
from services.parameters_validator import validate_pagination_parameters

from .models import PublisherVerificationRequests
from users.models import User
from .serializers import CreatePublisherVerificationRequestSerializer, PublisherVerificationRequestSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_publisher_verification_requests(request):
    try:
        user = request.user
        if user.account_type != "admin":
            return Response(
                {"error": "ليس لديك صلاحية لعرض طلبات التحقق"},
                status=status.HTTP_403_FORBIDDEN,
            )

        count, limit = validate_pagination_parameters(
            request.query_params.get("count", 0),
            request.query_params.get("limit", 7),
        )

        verification_requests_qs = (
            PublisherVerificationRequests.objects.filter(status="pending").order_by("-created_at")

        )

        total_count = verification_requests_qs.count()

        start = count * limit
        end = (count + 1) * limit

        if start > total_count:
            start = total_count
        if end > total_count:
            end = total_count

        serializer = PublisherVerificationRequestSerializer(
            verification_requests_qs[start:end],
            many=True,
        )

        return Response(
            {
                "verification_requests": serializer.data,
                "total_number": total_count,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_publisher_verification_request(request):
   
    try:
        user = request.user
        user = get_object_or_404(User, id=user.id)
        
        if user.account_type != "teacher" and user.account_type != "team":
            return Response(
                {"error": "ليس لديك صلاحية لإنشاء طلب توثيق "},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        if not request.FILES.get("image1") or not request.FILES.get("image2"):
            return Response(
                {"error": "يجب إرفاق صورة الهوية لتوثيق الحساب"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        previous_verification_request = PublisherVerificationRequests.objects.filter(publisher_id=user, status="pending").first()
       
        if previous_verification_request:
            return Response(
                {"error": "لديك طلب توثيق سابق ينتظر الموافقة"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        previous_verification_request = PublisherVerificationRequests.objects.filter(publisher_id=user, status="approved").first()
        
        if previous_verification_request:
            return Response(
                {"error": "تم توثيق الحساب مسبقاً"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        serializer = CreatePublisherVerificationRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            image1 = serializer.validated_data.get("image1")
            image2 = serializer.validated_data.get("image2")
            PublisherVerificationRequests.objects.create(
                publisher_id=user,
                image1=image1,
                image2=image2,
            )
            return Response({"message": "تم إرسال طلب التوثيق بنجاح"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def approve_verification_request(request, request_public_id):
    """
    Approve a publisher verification request (admin only).
    """
    try:
        user = request.user
        if user.account_type != "admin":
            return Response(
                {"error": "ليس لديك صلاحية للموافقة على طلبات التحقق"},
                status=status.HTTP_403_FORBIDDEN,
            )

        verification_request = get_object_or_404(
            PublisherVerificationRequests, public_id=request_public_id
        )

        if verification_request.status != "pending":
            return Response(
                {"error": "تم معالجة هذا الطلب مسبقاً"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        verification_request.status = "approved"
        verification_request.processed_at = timezone.now()
        verification_request.save()
        user = verification_request.publisher_id
        user.is_verified = True
        user.save()

        serializer = PublisherVerificationRequestSerializer(verification_request)
        return Response(
            {"message": "تم الموافقة على طلب التحقق بنجاح", "request": serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def reject_verification_request(request, request_public_id):
    """
    Reject a publisher verification request (admin only).
    """
    try:
        user = request.user
        if user.account_type != "admin":
            return Response(
                {"error": "ليس لديك صلاحية لرفض طلبات التحقق"},
                status=status.HTTP_403_FORBIDDEN,
            )
            
        reason = request.data.get("reason", "")

        verification_request = get_object_or_404(
            PublisherVerificationRequests, public_id=request_public_id
        )

        if verification_request.status != "pending":
            return Response(
                {"error": "تم معالجة هذا الطلب مسبقاً"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        verification_request.status = "rejected"
        verification_request.processed_at = timezone.now()
        verification_request.save()
        
        # notify user why did not approve
        Notifications.objects.create(
            receiver_id=verification_request.publisher_id,
            source_type="siraj-management",
            title="تم رفض طلب التوثيق",
            content="تم رفض طلب التوثيق السبب : " + reason
        )

        serializer = PublisherVerificationRequestSerializer(verification_request)
        return Response(
            {"message": "تم رفض طلب التحقق بنجاح", "request": serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)