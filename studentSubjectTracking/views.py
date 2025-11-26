from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import StudentSubjectTracking
from .serializers import StudentSubjectTrackingSerializer
from users.models import User

@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_student_subject_tracking(request):
    try:
        student = get_object_or_404(User, id=request.user.id)
        Class = request.data.get("Class")

        subject_tracking = StudentSubjectTracking.objects.filter(
            student_id=student,
            Class=Class,
        )

        serializer = StudentSubjectTrackingSerializer(subject_tracking, many=True)
        return Response(
            {"student_subject_tracking": serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
