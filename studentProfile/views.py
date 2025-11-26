from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView


from .models import StudentProfile
from .serializers import (
    OwnStudentProfileSerializer,
    PublicStudentProfileSerializer,
    StudentProfileUpdateSerializer,
)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def increase_number_of_done_exams(request, user_id):
    """
    increase the number of applied exams for a student
    """

    student = StudentProfile.objects.get(user=user_id)
    student.number_of_done_exams += 1
    student.save()

    return Response(
        {"message": "تم زيادة عدد الامتحانات المقدمة بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def increase_number_of_read_notes(request, user_id):
    """
    increase the number of read notes for a student
    """
    student = StudentProfile.objects.get(user=user_id)
    student.number_of_read_notes += 1
    student.save()

    return Response(
        {"message": "تم زيادة عدد النوط المقروءة بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def increase_number_of_completed_courses(request, user_id):
    """
    increase the number of completed courses for a student
    """
    student = StudentProfile.objects.get(user=user_id)
    student.number_of_completed_courses += 1
    student.save()

    return Response(
        {"message": "تم زيادة عدد الدورات المكملة بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_student_profile(request, user_id):
    """
    Endpoint to update student profile information
    Supports both PUT (full update) and PATCH (partial update)
    the request is something like this:
    {
        "user": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "city": "New York",
            "image": "https://example.com/image.jpg",
        }
        "Class": "12",
        "school": "Harvard University",
    }
    """
    user = request.user
    profile = StudentProfile.objects.get(user=user)
    serializer = StudentProfileUpdateSerializer(profile, data=request.data , partial=True)

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
        
    serializer.save()
    
    return Response(
        {"message": "تم تحديث الملف الشخصي بنجاح"},
        status=status.HTTP_200_OK,
    )


class public_student_profile(APIView):

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_student_profile"

    def get(self, request, student_id):

        try:

            student = StudentProfile.objects.get(user=student_id)
            serializer = PublicStudentProfileSerializer(student)
            return Response(serializer.data, status=200)

        except StudentProfile.DoesNotExist:
            return Response(
                {"error": "ملف الطالب غير موجود"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"حدث خطأ أثناء جلب ملف الطالب: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def own_student_profile(request, user_id):
    """ """
    try:
        student = StudentProfile.objects.get(user=user_id)
        serializer = OwnStudentProfileSerializer(student)
        return Response(serializer.data, status=200)
    except StudentProfile.DoesNotExist:
        return Response(
            {"error": "ملف الطالب غير موجود"}, status=status.HTTP_404_NOT_FOUND
        )
