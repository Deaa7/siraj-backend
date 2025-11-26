from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import GetLessonSerializer, LessonSerializer
from .models import Lessons


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_lesson(request):
    serializer = LessonSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_lessons(request , course_id):
    lessons = Lessons.objects.filter(course_id=course_id)
    serializer = GetLessonSerializer(lessons, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



