from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User
from .models import Followers


 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_user(request, public_user_id):
    follower = request.user
    followed = get_object_or_404(User, uuid=public_user_id)

    if follower == followed:
        return Response(
            {"error": "لا يمكنك متابعة نفسك"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if Followers.objects.filter(follower_id=follower, followed_id=followed).exists():
        return Response(
            {"message": "تمت المتابعة مسبقًا"},
            status=status.HTTP_200_OK,
        )

    Followers.objects.create(
        follower_id=follower,
        followed_id=followed,
    )
    
    followed.number_of_followers += 1
    followed.save()

    return Response(
        {"message": "تمت المتابعة بنجاح"},
        status=status.HTTP_201_CREATED,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def unfollow_user(request, public_user_id):
    follower = request.user
    followed = get_object_or_404(User, uuid=public_user_id)

    follow_relation = Followers.objects.filter(
        follower_id=follower,
        followed_id=followed,
    ).first()

    if not follow_relation:
        return Response(
            {"error": "لم يتم العثور على متابعة لهذا المستخدم"},
            status=status.HTTP_404_NOT_FOUND,
        )

    follow_relation.delete()
    followed.number_of_followers -= 1
    followed.save()

    return Response(
        {"message": "تم إلغاء المتابعة بنجاح"},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def is_following_user(request, public_user_id):
    follower = request.user
    followed_exists = User.objects.filter(uuid=public_user_id).exists()

    if not followed_exists:
        return Response(
            {"error": "المستخدم غير موجود"},
            status=status.HTTP_404_NOT_FOUND,
        )

    is_following = Followers.objects.filter(
        follower_id=follower,
        followed_id__uuid=public_user_id,
    ).exists()

    return Response(
        {"is_following": is_following},
        status=status.HTTP_200_OK,
    )