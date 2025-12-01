from rest_framework.views import APIView
from teamProfile.serializers import (
    OwnTeamProfileSerializer,
    PublicTeamProfileSerializer,
    TeamProfileUpdateSerializer,
    TeamUserUpdateSerializer,
)
from .models import TeamProfile
from users.models import User

from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.permissions import IsAuthenticated

# Create your views here.


@api_view(["POST"])
def change_number_of_exams(request):
    """
    Change the number of exams for a team ,  number is either 1 or -1
    """
    user = request.data.get("id")
    number = request.data.get("number")
    team = TeamProfile.objects.get(user=user)
    team.number_of_exams += number
    team.save()

    return Response(
        {"message": "تم تعديل عدد الامتحانات بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
def change_number_of_notes(request):
    """
    Change the number of notes for a team ,  number is either 1 or -1
    """
    user = request.data.get("id")
    number = request.data.get("number")
    team = TeamProfile.objects.get(user=user)
    team.number_of_notes += number
    team.save()

    return Response(
        {"message": "تم تعديل عدد الملاحظات بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
def change_number_of_courses(request):
    """
    Change the number of courses for a team ,  number is either 1 or -1
    """
    user = request.data.get("id")
    number = request.data.get("number")
    team = TeamProfile.objects.get(user=user)
    team.number_of_courses += number
    team.save()

    return Response(
        {"message": "تم تعديل عدد الكورسات بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
def change_number_of_followers(request):
    """
    Change the number of followers for a team , number is either 1 or -1
    """
    user = request.data.get("id")
    number = request.data.get("number")
    team = TeamProfile.objects.get(user=user)
    team.number_of_followers += number
    team.save()

    return Response(
        {"message": "تم تعديل عدد المتابعين بنجاح"}, status=status.HTTP_200_OK
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_team_profile(request):
    """
    Endpoint to update team profile information
    Supports both PUT (full update) and PATCH (partial update)
    the request is something like this:
    {
        "user": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "team_name": "Team 1",
            "city": "New York",
        }
        "address": "123 Main St, Anytown, USA",
        "bio": "We are a team of 10 people who are passionate about technology",
        "years_of_experience": 10,
        "telegram_link": "https://t.me/team1",
        "whatsapp_link": "https://wa.me/1234567890",
        "instagram_link": "https://www.instagram.com/team1",
    }
    """
    user = request.user
    user = User.objects.get(id = user.id)
    profile = TeamProfile.objects.get(user=user)
    
    serializer = TeamProfileUpdateSerializer(profile, data=request.data)
    user_serializer = TeamUserUpdateSerializer(user , data=request.data["user"] , partial=True )
    
    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
        
    if not user_serializer.is_valid():
        return Response(
            {"errors": user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    serializer.save()
    user_serializer.save()
    
    return Response(
        {"message": "تم تحديث الملف الشخصي بنجاح"},
        status=status.HTTP_200_OK,
    )


class public_team_profile(APIView):

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_team_profile"

    def get(self, request, team_uuid: str):
        """
        Get a public team profile
        Rate limited to 10 requests per minute per IP address
        """

        try:

            team = TeamProfile.objects.get(user__uuid=team_uuid)
            serializer = PublicTeamProfileSerializer(team)
            return Response(serializer.data, status=200)

        except TeamProfile.DoesNotExist:
            return Response(
                {"error": "ملف المعلم غير موجود"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"حدث خطأ أثناء جلب ملف المعلم: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def own_team_profile(request):
    """
    Get an own team profile
    """
    try:
        team = TeamProfile.objects.get(user=request.user)
        serializer = OwnTeamProfileSerializer(team)
        return Response(serializer.data, status=200)
    except TeamProfile.DoesNotExist:
        return Response(
            {"error": "ملف الفريق غير موجود"}, status=status.HTTP_404_NOT_FOUND
        )
