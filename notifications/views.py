from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Notifications

from .serializers import NotificationListSerializer

from services.parameters_validator import validate_pagination_parameters


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_public_id):
    """
    Mark a notification as read for the authenticated user.
    """
    try:
        notification = get_object_or_404(
            Notifications,
            public_id=notification_public_id,
            receiver_id=request.user,
        )

        if not notification.read:
            notification.read = True
            notification.save(update_fields=["read"])

        return Response({"message": "تم تعليم الإشعار كمقروء"}, status=status.HTTP_200_OK)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_public_id):
    """
    Delete a notification for the authenticated user.
    """
    try:
        notification = get_object_or_404(
            Notifications,
            public_id=notification_public_id,
            receiver_id=request.user,
        )

        notification.delete()

        return Response({"message": "تم حذف الإشعار"}, status=status.HTTP_200_OK)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_notifications_list(request):
    """
    Return paginated notifications for the specified user (by public ID).
    """
    try:
      
        count , limit = validate_pagination_parameters(request.data.get("count", 0), request.data.get("limit", 7))

        notifications_qs = Notifications.objects.filter(
            receiver_id=request.user
        )

        total_number = notifications_qs.count()
        begin = count * limit
        end = (count + 1) * limit

        if begin > total_number:
            begin = total_number
        if end > total_number:
            end = total_number

        serializer = NotificationListSerializer(
            notifications_qs[begin:end], many=True
        )

        return Response(
            {
                "notifications": serializer.data,
                "total_number": total_number,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
