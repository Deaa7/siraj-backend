from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Reports
from .serializers import ReportListSerializer

from services.parameters_validator import validate_pagination_parameters

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_report_list(request):
    """
    Return paginated list of unverified reports for admin users only.
    """
    try:
        user = request.user

        if user.account_type != "admin":
            return Response(
                {"error": "غير مصرح لك بالوصول"},
                status=status.HTTP_403_FORBIDDEN,
            )

        limit, count = validate_pagination_parameters(
            request.query_params.get("limit", 7),
            request.query_params.get("count", 0),
        )
        reports_qs = Reports.objects.filter(verified=False)
        total_count = reports_qs.count()
        
        begin = count * limit
        end = (count + 1) * limit
        
        if begin > total_count:
            begin = total_count
        
        if end > total_count:
            end = total_count
        
        serializer = ReportListSerializer(reports_qs[begin:end], many=True)

        return Response(
            {
                "reports": serializer.data,
                "total_number": total_count,
            },
            
            status=status.HTTP_200_OK,
        )
        
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def mark_report_as_verified(request, report_public_id):
    """
    Mark a report as verified (admin only).
    """
    try:
        user = request.user

        if user.account_type != "admin":
            return Response(
                {"error": "غير مصرح لك بالوصول"},
                status=status.HTTP_403_FORBIDDEN,
            )

        report = get_object_or_404(Reports, public_id=report_public_id)
        report.verified = True
        report.save()

        return Response({"message": "تم توثيق البلاغ بنجاح"}, status=status.HTTP_200_OK)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
