from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from services.parameters_validator import validate_pagination_parameters
from .serializers import StudentPremiumContentCardSerializer

# models 
from .models import StudentPremiumContent
from users.models import User


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_student_premium_content_cards(request):
    try:

        student = get_object_or_404(User, user = request.user)

        limit, count = validate_pagination_parameters(
            request.query_params.get("limit", 7),
            request.query_params.get("count", 0),
        )

        premium_content_qs = (
            StudentPremiumContent.objects.select_related(
                "exam_id",
                "note_id",
                "course_id",
                "publisher_id",
            )
            .filter(student_id=student)
        )

        total_count = premium_content_qs.count()

        start = count * limit
        end =  ( count +1 )*limit 

        if start > total_count:
            start = total_count
        if end > total_count:
            end = total_count

        serializer = StudentPremiumContentCardSerializer(
            premium_content_qs[start:end],
            many=True,
        )

        return Response(
            {
                "content": serializer.data,
                "total_count": total_count,
            },
            status=status.HTTP_200_OK,
        )
        
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)



