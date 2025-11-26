from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from teamProfile.serializers import TeamPreviewSerializer
from .models import TeacherProfile
from .serializers import (
    TeacherPreviewSerializer,
    TeacherProfileUpdateSerializer,
    PublicTeacherProfileSerializer,
    OwnTeacherProfileSerializer,
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.db.models import Q
from teamProfile.models import TeamProfile

 
# Create your views here.


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_number_of_exams(request):
    """
    Change the number of exams for a teacher ,  number is either 1 or -1
    """
    teacher_id=request.data.get("teacher_id")
    number = request.data.get("number")
    teacher = TeacherProfile.objects.get(id=teacher_id)
    teacher.number_of_exams += number
    teacher.save()

    return Response(
        {"message": "تم تعديل عدد الامتحانات بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_number_of_notes(request):
    """
    Change the number of notes for a teacher ,  number is either 1 or -1
    """
    teacher_id=request.data.get("teacher_id")
    number = request.data.get("number")
    teacher = TeacherProfile.objects.get(id=teacher_id)
    teacher.number_of_notes += number
    teacher.save()

    return Response(
        {"message": "تم تعديل عدد الملاحظات بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_number_of_courses(request):
    """
    Change the number of courses for a teacher ,  number is either 1 or -1
    """
    teacher_id=request.data.get("teacher_id")
    number = request.data.get("number")
    teacher = TeacherProfile.objects.get(id=teacher_id)
    teacher.number_of_courses += number
    teacher.save()

    return Response(
        {"message": "تم تعديل عدد الكورسات بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_number_of_followers(request):
    """
    Change the number of followers for a teacher , number is either 1 or -1
    """
    teacher_id=request.data.get("teacher_id")
    number = request.data.get("number")
    teacher = TeacherProfile.objects.get(id=teacher_id)
    teacher.number_of_followers += number
    teacher.save()

    return Response(
        {"message": "تم تعديل عدد المتابعين بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_teacher_profile(request):
    """
    Endpoint to update teacher profile information
    Supports both PUT (full update) and PATCH (partial update)
    
    the request is something like this:
    {
        "user": {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
            "gender": "M",
            "city": "New York",
            "image": "https://example.com/image.jpg",
        },
        "Class": "12",
        "studying_subjects": "math",
        "university": "Harvard University",
        "address": "123 Main St, Anytown, USA",
        "bio": "I am a teacher at Harvard University",
        "years_of_experience": 10,
    }
    """
    user = request.user
    profile = TeacherProfile.objects.get(user=user)
    
    serializer = TeacherProfileUpdateSerializer(profile, data=request.data , partial=True)

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    serializer.save()
      
    return Response(
            {"message": "تم تحديث الملف الشخصي بنجاح"},
            status=status.HTTP_200_OK,
        )



@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_teacher_preview_cards(request):
    
    """
    Get a filtered preview of teachers based on search criteria
    Returns paginated list of teachers matching the specified filters
    """
    # Get query parameters for filtering
    type = request.GET.get("type")
    Class = request.GET.get("Class")
    subject_name = request.GET.get("subject_name")
    city = request.GET.get("city")
    count = request.GET.get("count", 1)
    limit = request.GET.get("limit", 10)
    name = request.GET.get("name")
    order = request.GET.get("order")

    result = None
    if type == "teacher":
        result = TeacherProfile.objects.select_related("user").all()
    else:
        result = TeamProfile.objects.select_related("user").all()

    if Class is not None:
        if type == "teacher":
            result = result.filter(Class=Class)

    if name is not None:
        if type == "teacher":
            result = result.filter(user__full_name__icontains=name)
        else:
            result = result.filter(user__team_name__icontains=name)

    if city is not None:
        result = result.filter(user__city=city)

    if subject_name is not None and type == "teacher":
        if subject_name == "physics" or subject_name == "chemistry":
            result = result.filter(
                Q(studying_subjects=subject_name)
                | Q(studying_subjects="physics_chemistry")
            )
        else:
            result = result.filter(studying_subjects=subject_name)

    if order is not None:

        if order == "year_of_experience":
            result = result.order_by("-year_of_experience")
        elif order == "number_of_followers":
            result = result.order_by("-number_of_followers")
        elif order == "number_of_exams":
            result = result.order_by("-number_of_exams")
        elif order == "number_of_notes":
            result = result.order_by("-number_of_notes")
        elif order == "number_of_courses":
            result = result.order_by("-number_of_courses")

    if type == "teacher":
        serial = TeacherPreviewSerializer(result, many=True)
    else:
        serial = TeamPreviewSerializer(result, many=True)
    total_count = len(serial.data)

    begin = (int(count) - 1) * int(limit)
    end = int(count) * int(limit)

    paginated_data = serial.data[begin:end]

    return Response(
        {"Preview_cards": paginated_data, "number": total_count}, status=200
    )


class public_teacher_profile(APIView):
 
   throttle_classes = [ScopedRateThrottle]
   throttle_scope = 'public_teacher_profile'
   def get(self, request, teacher_uuid: str):
    try:
        
        teacher = TeacherProfile.objects.select_related("user").get(user__uuid=teacher_uuid)
        serializer = PublicTeacherProfileSerializer(teacher)
        return Response(serializer.data, status=200)
        
    except TeacherProfile.DoesNotExist:
        return Response(
            {"error": "ملف المعلم غير موجود"},
            status=status.HTTP_404_NOT_FOUND
        )
        
    except Exception as e:
        return Response(
            {"error": f"حدث خطأ أثناء جلب ملف المعلم: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def own_teacher_profile(request):
    """
    Get a own teacher profile
    """
    try:
        teacher = TeacherProfile.objects.select_related("user").get(id=request.user.id)
        serializer = OwnTeacherProfileSerializer(teacher)
        return Response(serializer.data, status=200)
    except TeacherProfile.DoesNotExist:
        return Response(
            {"error": "ملف المعلم غير موجود"},
            status=status.HTTP_404_NOT_FOUND
        )

