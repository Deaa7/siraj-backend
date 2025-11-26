from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourseStatusTrackingCardsSerializer
from .models import CourseStatusTracking
from courses.models import Course
from django.shortcuts import get_object_or_404
from studentSubjectTracking.models import StudentSubjectTracking


# create or update existing course status tracking for a student
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_course_status_tracking(request , course_public_id ):
    
   try:
       
    user = request.user # student info
    course = get_object_or_404(Course, public_id=course_public_id)  
    
    if user is None : 
        return Response({"error": "مستخدم غير موجود"}, status=status.HTTP_404_NOT_FOUND)
    
    course_status_tracking, created = CourseStatusTracking.objects.get_or_create(
        course_id=course,
        student_id=user,
        publisher_id=course.publisher_id,
    )

    if created:
        subject_tracking = StudentSubjectTracking.objects.get(
            student_id=user,
            subject_name=course.subject_name,
        )
        subject_tracking.number_of_courses += 1
        subject_tracking.save()
    
    return Response( status=status.HTTP_200_OK)    
    
   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_course_status_tracking_cards(request,public_student_id) :
    
    try:
        limit = request.query_params.get('limit', 10)
        count = request.query_params.get('count', 0)
        limit = int(limit)
        count = int(count)
        
        begin = count * limit
        end = (count+1) * limit
        course_status_trackings = CourseStatusTracking.objects.select_related('course_id' , 'student_id').filter(student_id__uuid=public_student_id)
        
        serializer = CourseStatusTrackingCardsSerializer(course_status_trackings[begin:end], many=True)
        
        return Response({"course_tracking_cards": serializer.data, "count": len(course_status_trackings)}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def is_student_enrolled_in_course(request,public_student_id,public_course_id) :
    try:
        student = get_object_or_404(User, public_id=public_student_id)
        course = get_object_or_404(Course, public_id=public_course_id)
        course_status_tracking = CourseStatusTracking.objects.get(student_id=student, course_id=course).exists()
        return Response({"is_enrolled": course_status_tracking}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# @permission_classes([IsAuthenticated])
# @api_view(['PATCH'])
# def increase_number_of_completed_lessons(request , course_public_id ):
    
#     try:
#         user = request.user # student info
#         course = get_object_or_404(Course, public_id=course_public_id)  
        
#         if user is None : 
#             return Response({"error": "مستخدم غير موجود"}, status=status.HTTP_404_NOT_FOUND)
        
#         course_status_tracking = get_object_or_404(CourseStatusTracking, course_id=course, student_id=user)
#         course_status_tracking.number_of_completed_lessons += 1
        
#         if course_status_tracking.number_of_completed_lessons >= course.number_of_lessons:
        
#             course_status_tracking.complete = True
#             course_status_tracking.complete_date = datetime.now()
#             course.number_of_completions += 1
#             course.save()
        
#         course_status_tracking.save()
#         return Response( status=status.HTTP_200_OK)
        
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
 
 