 
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import GetLessonSerializer, LessonSerializer, UpdateLessonSerializer
from .models import Lessons
from django.shortcuts import get_object_or_404
from videos.serializers import CreateVideoSerializer
from videos.models import Videos
from courses.models import Course


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_lesson(request, course_public_id):
    course = get_object_or_404(Course, public_id=course_public_id)
    
    # 1. Always copy request.data if you plan to modify it
    request.data['course_id'] = course.id
    request.data['url'] = request.data['content_public_id']
    print("here is request.data", request.data)
    serializer = LessonSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            # Extract validated data
            lesson_type = serializer.validated_data.get('lesson_type')
            content_public_id = serializer.validated_data.get('content_public_id')
 
            # 2. Logic for Video Type
            if lesson_type == 'video':
                videoData =  CreateVideoSerializer(data=request.data)
                if videoData.is_valid():
                    
                    video = Videos.objects.create(
                        publisher_id=request.user,  # Pass the user object
                        url=content_public_id,     # This is the raw URL from front-end
                        name=videoData.validated_data.get('name', ''),
                        explanation=videoData.validated_data.get('explanation', '')
                    )
                    # Overwrite content_public_id with the new Video's public_id
                    
                    content_public_id = video.public_id
                else:
                    return Response(videoData.errors, status=status.HTTP_400_BAD_REQUEST)
            # 3. Save Lesson
            # Pass extra attributes directly to save()
            
            # SUCCESS RETURN
            print("here is the lesson creation " )
            Lessons.objects.create(
                    course_id=course,
                    lesson_type=lesson_type,
                    content_public_id=content_public_id,
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # ERROR DURING PROCESSING RETURN
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # INVALID DATA RETURN
    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_lessons(request , course_id):
    lessons = Lessons.objects.filter(course_id=course_id)
    serializer = GetLessonSerializer(lessons, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def update_lesson(request , lesson_public_id):
    """
    
    request.data:
        lesson_type : string (exam | note | video)
        content_public_id : string // may be url for video or public_id for exam or note
        explanation : string | null
        name : string | null
    """
    try:
        publisher_id = request.user.id
        lesson = get_object_or_404(Lessons, public_id=lesson_public_id)
            
        request.data['publisher_id'] = publisher_id
   
        lesson_data = request.data
    
        lesson_data_copy = lesson_data.copy()

        video = None
                    
        if  lesson_data_copy['lesson_type'] == 'video': 
            lesson_data_copy['publisher_id'] = publisher_id
            lesson_data_copy['url'] = lesson_data_copy['content_public_id']
            videoData =  CreateVideoSerializer(data=lesson_data_copy)
            
            if videoData.is_valid():
                video = videoData.save()
                lesson_data_copy['content_public_id'] = video.public_id
            else:
              return Response(videoData.errors, status=status.HTTP_400_BAD_REQUEST)
                                            
        lesson_serializer = UpdateLessonSerializer(lesson, data=lesson_data_copy)
        if lesson_serializer.is_valid():
          lesson_serializer.save()
          return Response(lesson_serializer.data, status=status.HTTP_200_OK)
        else:
          return Response(lesson_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Lessons.DoesNotExist:
        return Response({"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_lesson(request , lesson_public_id):
    lesson = get_object_or_404(Lessons, public_id=lesson_public_id)
    lesson.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)