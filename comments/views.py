from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Comment
from .serializers import (
    CommentCreateSerializer,
    CommentListSerializer,
    CommentUpdateSerializer,
)
from users.models import User
from exams.models import Exam
from notes.models import Note
from courses.models import Course
from posts.models import Post
from notifications.tasks import publishing_comment_notification
from django.shortcuts import get_object_or_404




@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_comment(request):
    """
    Create a comment on exam, note, course, post, or another comment.
    Returns the public_id of the created comment.
    """
    serializer = CommentCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user: User = request.user
    content_type = serializer.validated_data["content_type"]
    content_public_id = serializer.validated_data["content_public_id"]
    comment_text = serializer.validated_data["comment_text"]

    contentObj = None 
    comment = None
    if content_type == "exam" :
      
      contentObj = get_object_or_404(Exam, public_id = content_public_id)
      contentObj.number_of_comments += 1
      contentObj.save()
      commnet = Comment.objects.create(user_id = user, comment_text = comment_text, exam_id = contentObj)
      
    elif content_type == "note" :
      
      contentObj = get_object_or_404(Note, public_id = content_public_id)
      contentObj.number_of_comments += 1
      contentObj.save()
      comment = Comment.objects.create(user_id = user, comment_text = comment_text, note_id = contentObj)
      
      
    elif content_type == "course" :
        
      contentObj = get_object_or_404(Course, public_id = content_public_id)
      contentObj.number_of_comments += 1
      contentObj.save()
      comment = Comment.objects.create(user_id = user, comment_text = comment_text, course_id = contentObj)
      
    elif content_type == "post" :
    
      contentObj = get_object_or_404(Post, public_id = content_public_id)
      contentObj.number_of_comments += 1
      contentObj.save()
      comment = Comment.objects.create(user_id = user, comment_text = comment_text, post_id = contentObj)
      
    
    elif content_type == "comment":
      
        contentObj = get_object_or_404(Comment, public_id = content_public_id)
        contentObj.number_of_replies += 1
        contentObj.save()
        comment = Comment.objects.create(user_id = user, comment_text = comment_text, comment_id = contentObj)
      
    else:
        return Response(
            {"error": "نوع المحتوى غير معروف"},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
 
    publishing_comment_notification.delay(comment.id, user , content_type, content_public_id , contentObj.name)

    return Response(comment.public_id, status=status.HTTP_201_CREATED)


@permission_classes([IsAuthenticated])
@api_view(["PATCH", "PUT"])
def update_comment(request, comment_public_id):
    """
    # Update comment text (owner or admin only).
    """
    comment = get_object_or_404(Comment.objects.select_related("user_id"), public_id=comment_public_id)
    user: User = request.user

    if comment.user_id != user:
        return Response(
            {"error": "غير مصرح لك بتعديل هذا التعليق"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = CommentUpdateSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    comment_text = serializer.validated_data.get("comment_text")

    if comment_text is not None:
        comment.comment_text = comment_text
        comment.save()

    return Response({"message": "تم تعديل التعليق بنجاح"}, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_comment(request, comment_public_id):
    """
    Delete a comment (owner or admin only).
    """
    comment = get_object_or_404(Comment, public_id=comment_public_id)
    user: User = request.user

    if comment.user_id != user:
        return Response(
            {"error": "غير مصرح لك بحذف هذا التعليق"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if comment.comment_id is not None:
        comment.comment_id.number_of_replies -= 1
        comment.comment_id.save()
    elif comment.exam_id is not None:
        comment.exam_id.number_of_comments -= 1
        comment.exam_id.save()
    elif comment.note_id is not None:
        comment.note_id.number_of_comments -= 1
        comment.note_id.save()
    elif comment.course_id is not None:
       comment.course_id.number_of_comments -= 1
       comment.course_id.save()
    elif comment.post_id is not None:
        comment.post_id.number_of_comments -= 1
        comment.post_id.save()
    comment.delete()
   
    return Response({"message": "تم حذف التعليق بنجاح"}, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_content_comments(request, content_public_id):
    """
    Retrieve comments list for a given content_type and content_public_id.
    """
    content_type = request.data.get("content_type")
 
    limit, count = validate_pagination_parameters(request.data.get("count", 0), request.data.get("limit", 7))
 
    comments = None
    contentObj = None
 
    if content_type not in ["exam", "note", "course", "post", "comment"]:
        return Response(
            {"error": "نوع المحتوى غير صحيح"},
            status=status.HTTP_400_BAD_REQUEST,
        )
 
    
    if content_type == "exam":
      contentObj = get_object_or_404(Exam, public_id = content_public_id)
      comments = Comment.objects.filter(exam_id = contentObj)
    elif content_type == "note":
      contentObj = get_object_or_404(Note, public_id = content_public_id)
      comments = Comment.objects.filter(note_id = contentObj)
    elif content_type == "course":
      contentObj = get_object_or_404(Course, public_id = content_public_id)
      comments = Comment.objects.filter(course_id = contentObj)
    elif content_type == "post":
      contentObj = get_object_or_404(Post, public_id = content_public_id)
      comments = Comment.objects.filter(post_id = contentObj)
    elif content_type == "comment":
      contentObj = get_object_or_404(Comment, public_id = content_public_id)
      comments = Comment.objects.filter(comment_id = contentObj)
    else:
      return Response(
        {"error": "نوع المحتوى غير معروف"},
        status=status.HTTP_400_BAD_REQUEST,
      )
      
    begin = count * limit
    end = (count + 1) * limit
   
    if end > comments.count():
      end = comments.count()
   
    comments = comments[begin:end]

    serializer = CommentListSerializer(comments, many=True)
    
    return Response({"comments": serializer.data, "total_number": comments.count()}, status=status.HTTP_200_OK)
