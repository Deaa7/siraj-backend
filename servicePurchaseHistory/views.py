from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from services.parameters_validator import validate_pagination_parameters

from .models import ServicePurchaseHistory
from .serializers import ServicePurchaseHistorySerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_service_purchase_history(request):
    try:
     
        user = request.user
        if user.account_category != "admin":
            return Response(
                {"error": "ليس لديك صلاحية لعرض تاريخ الشراء"},
                status=status.HTTP_403_FORBIDDEN,
            )
            
        limit, count = validate_pagination_parameters(
            request.query_params.get("limit", 7),
            request.query_params.get("count", 0),
        )

        if limit <= 0:
            limit = 7
        if count < 0:
            count = 0

        purchase_history_qs = ServicePurchaseHistory.objects.filter(user_id=user)

        total_count = purchase_history_qs.count()

        start = count * limit
        end = (count + 1) * limit

        if start > total_count:
            start = total_count
        if end > total_count:
            end = total_count

        serializer = ServicePurchaseHistorySerializer(
            purchase_history_qs[start:end],
            many=True,
        )

        return Response(
            {
                "history": serializer.data,
                "total_count": total_count,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)



