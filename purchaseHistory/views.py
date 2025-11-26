from datetime import timedelta

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
def publisher_number_of_purchases_and_profit_last_month(request):
    """
    Return the number of purchases and the publisher profit grouped by date
    for the last 30 days for the authenticated publisher.
    """
    try:
        publisher: User = request.user
        now = timezone.now()
        start_date = now - timedelta(days=30)

        daily_summary = (
            PurchaseHistory.objects.filter(
                publisher_id=publisher,
                purchase_date__gte=start_date,
            )
            .annotate(purchase_date=TruncDate("purchase_date"))
            .values("purchase_date")
            .annotate(
                total_purchases=Count("id"),
                total_profit=Sum("publisher_profit"),
            )
            .order_by("purchase_date")
        )

        results = []
        for entry in daily_summary:
            purchase_date = entry["purchase_date"]
            if purchase_date is None:
                continue

            results.append(
                {
                    "date": purchase_date.isoformat(),
                    "total_purchases": entry["total_purchases"],
                    "total_profit": str(entry["total_profit"] or 0),
                }
            )

        return Response(
            {
                "publisher_id": str(publisher.uuid),
                "period_start": start_date.date().isoformat(),
                "period_end": now.date().isoformat(),
                "daily_summary": results,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def publisher_purchases_grouped_by_gender_and_city_last_month(request):
    """
    Return the number of purchases in the last 30 days grouped by gender and
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

        gender_summary = (
            purchases_queryset.values("student_gender")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        city_summary = (
            purchases_queryset.values("student_city")
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
                "gender_distribution": gender_distribution,
                "city_distribution": city_distribution,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def content_purchase_history_dashboard_list(request):
    
    """
    Return paginated purchase history records for the authenticated publisher.
    """
    
    try:
        publisher: User = request.user
        limit, count = validate_pagination_parameters(
            request.query_params.get("limit", 7),
            request.query_params.get("count", 0),
        )
        purchase_records = PurchaseHistory.objects.filter(
            publisher_id=publisher
        )

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



