from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from services.parameters_validator import validate_pagination_parameters
from utils.validators import CommonValidators

#serializers
from .serializers import StudentSavedElementSerializer

#models 
from .models import StudentSavedElements
from exams.models import Exam
from notes.models import Note
from courses.models import Course


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def add_saved_element(request):
    try:
        user = request.user
        content_type = request.data.get("content_type")

        if content_type not in ["exam", "note", "course"]:
            return Response(
                {"error": "نوع المحتوى غير مدعوم"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        content_public_id = request.data.get("content_public_id")

        if not content_public_id:
            return Response(
                {"error": "يجب إرسال معرف المحتوى"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            content_public_id = CommonValidators.validate_username(
                content_public_id,
                "معرف المحتوى",
            )
            
        except ValidationError as validation_error:
            return Response(
                {"error": validation_error.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content_instance = None
        
        if content_type == "exam":
            content_instance = get_object_or_404(Exam, public_id=content_public_id)
        elif content_type == "note":
            content_instance = get_object_or_404(Note, public_id=content_public_id)
        elif content_type == "course":
            content_instance = get_object_or_404(Course, public_id=content_public_id)
        
        if content_type == "exam":
            StudentSavedElements.objects.create(student_id=user, type=content_type, exam_id=content_instance)
        elif content_type == "note":
            StudentSavedElements.objects.create(student_id=user, type=content_type, note_id=content_instance)
        elif content_type == "course":
            StudentSavedElements.objects.create(student_id=user, type=content_type, course_id=content_instance)
        
        return Response(status=status.HTTP_201_CREATED)
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        
        
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_saved_elements_cards(request):
    try:
        user = request.user
        limit, count = validate_pagination_parameters(request.query_params.get("limit", 7), request.query_params.get("count", 0))

        saved_elements_qs = StudentSavedElements.objects.select_related("exam_id", "note_id", "course_id").filter(student_id=user)

        total_count = saved_elements_qs.count()
        
        start = count * limit
        end = (count + 1) * limit
        
        if start > total_count:
            start = total_count
        if end > total_count:
            end = total_count
            
        serialized = StudentSavedElementSerializer(
            saved_elements_qs[start:end],
            many=True,
        )

        return Response(
            {
                "saved_elements": serialized.data,
                "total_count": total_count,
            },
            status=status.HTTP_200_OK,
        )
 
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_saved_element(request, saved_element_public_id):
    try:
        user = request.user
        
        saved_element = get_object_or_404(StudentSavedElements,  public_id=saved_element_public_id, student_id=user)

        saved_element.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
   
    except Exception as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
