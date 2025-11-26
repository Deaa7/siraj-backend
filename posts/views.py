from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Post
from users.models import User
from .serializers import (
    PostCreateSerializer,
    PostListSerializer,
    PostUpdateSerializer,
)
from notifications.tasks import publishing_post_notification


ALLOWED_PUBLISHER_TYPES = {"teacher", "team", "admin"}


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_post(request):
    """
    Create a new post for publisher accounts (teacher, team, admin).
    """
    user: User = request.user

    if user.account_type not in ALLOWED_PUBLISHER_TYPES:
        return Response(
            {"error": "غير مصرح لك بنشر منشور"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = PostCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    post = Post.objects.create(user=user, **serializer.validated_data)

    publishing_post_notification.delay(post.id, user)

    return Response(post.public_id, status=status.HTTP_201_CREATED)


@permission_classes([IsAuthenticated])
@api_view(["PATCH", "PUT"])
def update_post(request, post_public_id):
    """
    Update an existing post. Only the owner or an admin can update.
    """
    post = Post.objects.select_related('user').get(public_id = post_public_id)

    user: User = request.user
    
    if user.account_type not in ALLOWED_PUBLISHER_TYPES or post.user.id != user.id :
        return Response(
            {"error": "غير مصرح لك بتعديل هذا المنشور"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = PostUpdateSerializer(post, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    return Response("تم تعديل المنشور بنجاح", status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_post(request, post_public_id):
    """
    Delete a post. Only the owner or an admin can delete.
    """
    post = get_object_or_404(Post.objects.select_related("user"), public_id=post_public_id)

    user: User = request.user
    if user.account_type not in ALLOWED_PUBLISHER_TYPES or user.id != post.user :
        return Response(
            {"error": "غير مصرح لك بحذف هذا المنشور"},
            status=status.HTTP_403_FORBIDDEN,
        )

    post.delete()
    return Response(
        {"message": "تم حذف المنشور بنجاح"},
        status=status.HTTP_200_OK,
    )


 

@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_posts_list(request):
    """
    Retrieve a paginated list of posts 
    """
 
    count = request.query_params.get("count", request.data.get("count", 0))
    limit = request.query_params.get("limit", request.data.get("limit", 10))

    try:
        count = int(count)
        limit = int(limit)
    except (TypeError, ValueError):
        return Response(
            {"error": "قيم العد والحد يجب أن تكون أرقام صحيحة"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    posts = Post.objects.select_related("user").filter(active = True)
 
  
    total_count = posts.count()
    begin = count * limit
    end = begin + limit

    if begin > total_count:
        begin = total_count
    if end > total_count:
        end = total_count

    serializer = PostListSerializer(
        posts[begin:end],
        many=True,
    )

    return Response(
        {
            "posts": serializer.data,
            "total_number": total_count,
        },
        status=status.HTTP_200_OK,
    )


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_posts_by_publisher(request, publisher_public_id):
    """
    Retrieve posts for a specific publisher by public UUID with pagination.
    """
    count = request.query_params.get("count", request.data.get("count", 0))
    limit = request.query_params.get("limit", request.data.get("limit", 10))

    try:
        count = int(count)
        limit = int(limit)
    except (TypeError, ValueError):
        return Response(
            {"error": "قيم العد والحد يجب أن تكون أرقام صحيحة"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    posts = Post.objects.select_related("user").filter(
        user__uuid=publisher_public_id
    )

    total_count = posts.count()
    begin = count * limit
    end = begin + limit

    if begin > total_count:
        begin = total_count
    if end > total_count:
        end = total_count

    serializer = PostListSerializer(
        posts[begin:end],
        many=True,
    )

    return Response(
        {
            "posts": serializer.data,
            "total_number": total_count,
        },
        status=status.HTTP_200_OK,
    )


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def change_number_of_comments(request, post_public_id):
    """
    Change number of comments for a post (increment/decrement).
    """
    post = get_object_or_404(Post, public_id=post_public_id)
    number = request.data.get("number", 1)

    try:
        number = int(number)
    except (TypeError, ValueError):
        return Response(
            {"error": "قيمة number يجب أن تكون رقماً صحيحاً"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    post.number_of_comments = max(0, post.number_of_comments + number)
    post.save(update_fields=["number_of_comments"])

    return Response(status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def toggle_post_active(request, post_public_id):
    """
    Toggle post active status.
    """
    post = get_object_or_404(Post.objects.select_related("user"), public_id=post_public_id)

    user: User = request.user
    
    if user.account_type not in ALLOWED_PUBLISHER_TYPES or user.id != post.user:
        return Response(
            {"error": "غير مصرح لك بتعديل حالة هذا المنشور"},
            status=status.HTTP_403_FORBIDDEN,
        )

    post.active = not post.active
    post.save(update_fields=["active"])

    return Response(
        {"message": "تم تحديث حالة المنشور", "active": post.active},
        status=status.HTTP_200_OK,
    )
