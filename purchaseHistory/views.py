from datetime import timedelta, date, datetime

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# models : 
from .models import PurchaseHistory
from users.models import User

# serializer 
from .serializers import PurchaseHistoryDashboardSerializer

#services
from services.parameters_validator import validate_pagination_parameters


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def publisher_number_of_purchases_last_month(request):
    """
    Return the number of purchases grouped by date
    for the last 30 days for the authenticated publisher.
    Includes all dates in the range, with 0 for dates with no purchases.
    """
    try:
        publisher: User = request.user
        now = timezone.now()
        start_date = now - timedelta(days=30)

        # Generate all dates in the range [current_date - 30 days, current_date]
        current_date = timezone.localtime(now).date()
        start_date_only = start_date.date() if isinstance(start_date, datetime) else start_date

        # Initialize date_stats with all dates in the range, set to 0
        date_stats = {}
        for i in range(31):  # 30 days + current day = 31 days
            date_key = (start_date_only + timedelta(days=i)).isoformat()
            date_stats[date_key] = {
                "date": date_key,
                "total_purchases": 0,
            }

        # Get actual purchase data
        daily_summary = (
            PurchaseHistory.objects.filter(
                publisher_id=publisher,
                purchase_date__gte=start_date,
            )
            .annotate(date_truncated=TruncDate("purchase_date"))
            .values("date_truncated")
            .annotate(
                total_purchases=Count("id"),
            )
        )

        # Update date_stats with actual data
        for entry in daily_summary:
            purchase_date = entry["date_truncated"]
            if purchase_date is None:
                continue

            date_key = purchase_date.isoformat()
            if date_key in date_stats:
                date_stats[date_key]["total_purchases"] = entry["total_purchases"]

        # Convert to list and sort by date (newest first)
        results = sorted(
            date_stats.values(), key=lambda item: item["date"], reverse=True
        )

        return Response(
            {
                "publisher_id": str(publisher.uuid),
                "period_start": start_date_only.isoformat(),
                "period_end": current_date.isoformat(),
                "number_of_purchases": results,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def publisher_profit_last_month(request):
    """
    Return the publisher profit grouped by date
    for the last 30 days for the authenticated publisher.
    Includes all dates in the range, with 0 for dates with no purchases.
    """
    try:
        publisher: User = request.user
        now = timezone.now()
        start_date = now - timedelta(days=30)

        # Generate all dates in the range [current_date - 30 days, current_date]
        current_date = timezone.localtime(now).date()
        start_date_only = start_date.date() if isinstance(start_date, datetime) else start_date

        # Initialize date_stats with all dates in the range, set to 0
        date_stats = {}
        for i in range(31):  # 30 days + current day = 31 days
            date_key = (start_date_only + timedelta(days=i)).isoformat()
            date_stats[date_key] = {
                "date": date_key,
                "total_profit": "0",
            }

        # Get actual profit data
        daily_summary = (
            PurchaseHistory.objects.filter(
                publisher_id=publisher,
                purchase_date__gte=start_date,
            )
            .annotate(date_truncated=TruncDate("purchase_date"))
            .values("date_truncated")
            .annotate(
                total_profit=Sum("publisher_profit"),
            )
        )

        # Update date_stats with actual data
        for entry in daily_summary:
            purchase_date = entry["date_truncated"]
            if purchase_date is None:
                continue

            date_key = purchase_date.isoformat()
            if date_key in date_stats:
                date_stats[date_key]["total_profit"] = str(entry["total_profit"] or 0)

        # Convert to list and sort by date (newest first)
        results = sorted(
            date_stats.values(), key=lambda item: item["date"], reverse=True
        )

        return Response(
            {
                "publisher_id": str(publisher.uuid),
                "period_start": start_date_only.isoformat(),
                "period_end": current_date.isoformat(),
                "profit": results,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def publisher_purchases_grouped_by_city_last_month(request):
    """
    Return the number of purchases in the last 30 days grouped 
    by city for the authenticated publisher.
    """
    try:
        publisher: User = request.user
        now = timezone.now()
        start_date = now - timedelta(days=30)

        purchases_queryset = PurchaseHistory.objects.filter(
            publisher_id=publisher,
            purchase_date__gte=start_date,
        )

    
        city_summary = (
            purchases_queryset.values("student_city")
            .annotate(total=Count("id"))
            .order_by("-total")
        )


        city_distribution = [
            {
                "city": entry["student_city"] or "unknown",
                "total_purchases": entry["total"],
            }
            for entry in city_summary
        ]

        return Response(
            {
                "publisher_id": str(publisher.uuid),
                "period_start": start_date.date().isoformat(),
                "period_end": now.date().isoformat(),
                "city_distribution": city_distribution,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
   
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def publisher_purchases_grouped_by_gender_last_month(request):
    """
    Return the number of purchases in the last 30 days grouped by gender 
    for the authenticated publisher.
    """
    try:
        publisher: User = request.user
        now = timezone.now()
        start_date = now - timedelta(days=30)

        purchases_queryset = PurchaseHistory.objects.filter(
            publisher_id=publisher,
            purchase_date__gte=start_date,
        )

        gender_summary = (
            purchases_queryset.values("student_gender")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

 
        gender_distribution = [
            {
                "gender": entry["student_gender"] or "unknown",
                "total_purchases": entry["total"],
            }
            for entry in gender_summary
        ]

    
        return Response(
            {
                "publisher_id": str(publisher.uuid),
                "period_start": start_date.date().isoformat(),
                "period_end": now.date().isoformat(),
                "gender_distribution": gender_distribution,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def purchase_history_list(request):
    
    """
    Return paginated purchase history records for the authenticated publisher.
    """
    
    try:
        publisher: User = request.user
        count, limit = validate_pagination_parameters(
            request.query_params.get("count", 0),
            request.query_params.get("limit", 7),
        )
        purchase_records = PurchaseHistory.objects.filter(
            publisher_id=publisher
        ).order_by("-created_at")

        total_number = purchase_records.count()

        begin = count * limit
        end = (count + 1) * limit

        if begin > total_number:
            begin = total_number
        if end > total_number:
            end = total_number

        serializer = PurchaseHistoryDashboardSerializer(
            purchase_records[begin:end], many=True
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



