
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status

from django.utils import timezone
from django.shortcuts import get_object_or_404


#tasks
from notifications.tasks import publishing_course_notification

#models 
from .models import Course
from lessons.models import Lessons
from users.models import User
from teacherProfile.models import TeacherProfile
from teamProfile.models import TeamProfile
from studentPremiumContent.models import StudentPremiumContent
from courseStatusTracking.models import CourseStatusTracking


#serializers
from lessons.serializers import GetLessonSerializer
from .serializers import (
    CourseCreateSerializer,
    CourseDetailSerializer,
    CourseDetailsForDashboardSerializer,
    CourseListDashboardSerializer,
    CourseListParametersSerializer,
    CourseListSerializer,
    CoursePreviewListSerializer,
    CourseUpdateSerializer,
)

#services
from services.publisher_plan_check import (
    check_publisher_plan,
    check_publishing_content_availability,
)


from services.parameters_validator import validate_pagination_parameters
from utils.validators import CommonValidators
from Constants import CLASSES_ARRAY, SUBJECT_NAMES_ARRAY, LEVELS_ARRAY

@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def increase_number_of_purchases(request, course_public_id):
   
    try:

        course = Course.objects.get(public_id=course_public_id)
        course.number_of_purchases += 1
        course.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def increase_number_of_enrollments(request, course_public_id):
    
    try:
        course = Course.objects.get(public_id=course_public_id)
        course.number_of_enrollments += 1
        course.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def increase_number_of_completions(request, course_public_id):

    try:
        course = Course.objects.get(public_id=course_public_id)
        course.number_of_completions += 1
        course.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def change_number_of_comments(request, course_public_id):
    try:
        number = request.data.get("number", 1)
        course = Course.objects.get(public_id=course_public_id)
        course.number_of_comments += number
        course.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# @permission_classes([IsAuthenticated])
# @api_view(["PATCH"])
# def change_number_of_likes(request, course_id):
#     try:
#         number = request.data.get("number", 1)
#         course = Course.objects.get(id=course_id)
#         course.number_of_likes += number
#         course.save()
#         return Response(status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_course(request):
    # publisher
  try:
    user = get_object_or_404(User, id=request.user.id)
    publisher_id = user.id
    publisher_type = user.account_type
    
    if not check_publishing_content_availability(
        publisher_id, publisher_type, "course"
    ):
        return Response(
            {"error": "لقد تجاوزت الحد المسموح به لنشر الدورات"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = CourseCreateSerializer(data=request.data)
    if serializer.is_valid():
        course = serializer.save()
        

        publishing_course_notification.delay(course.id, user)
        
        return Response(status=status.HTTP_201_CREATED)
    else :
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH", "PUT"])
def update_course(request, course_public_id):

    try:
        
        publisher_id = request.user.id
        course = get_object_or_404(Course, public_id=course_public_id)

        if course.publisher_id != publisher_id:
            return Response(
                {"error": "غير مصرح لك بتحديث هذه الدورة"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Pass the instance to the serializer for update
        serializer = CourseUpdateSerializer(course, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_course_details (request, course_public_id):

   """
    workflow: 
    -check if the student is enrolled in the course 
    -check if the student has purchased the course 
    -check if the course is active (if student has enrolled in this course before or has purchased it then return the course details)
    
   """
   try:
    
    source = request.data.get("source") # purchase | course | public
    course = get_object_or_404(Course, public_id=course_public_id)
    check_publisher_plan(course.publisher_id, "course")
    
    user = get_object_or_404(User, id=request.user.id) 
       
     
     # here after we check the plan, we get the course again to make sure it is still active
    course = Course.objects.select_related("publisher_id").get(public_id=course_public_id)    
   
    serializer = CourseDetailSerializer(course)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if not serializer.data["active"] :
     if source == "public":
        return Response(
            {"error": "عذراً هذه الدورة لم تعد متوفرة"},
            status=status.HTTP_400_BAD_REQUEST,
        )
  
    is_entered_before = CourseStatusTracking.objects.get(course_id=course.id, student_id=user.id).exists()
    is_purchased_before = True # free course case
    
    if serializer.data["price"] > 0:
        student_premium_content = StudentPremiumContent.objects.get(course_id=course.id, student_id=user.id).exists()

        if student_premium_content and student_premium_content.date_of_expiration > timezone.now():
            is_purchased_before = True

        else:
            is_purchased_before = False
            if student_premium_content:
             student_premium_content.delete()
   
   
    return Response({"course": serializer.data, "is_entered_before": is_entered_before, "is_purchased_before": is_purchased_before}, status=status.HTTP_200_OK)
  
   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_course_cards(request):

   try:
    serializer = CourseListParametersSerializer(data=request.data)
   
    if serializer.is_valid():
   
        publisher_name = serializer.validated_data.get("publisher_name")
        course_name = serializer.validated_data.get("course_name")
        Class = serializer.validated_data.get("Class")
        subject_name = serializer.validated_data.get("subject_name")
        level = serializer.validated_data.get("level")
        price = serializer.validated_data.get("price")
        order_by = serializer.validated_data.get("order_by")
   
        limit, count = validate_pagination_parameters(request.data.get("count", 0), request.data.get("limit", 7))
         
         
        publisher_name = CommonValidators.validate_arabic_text_field(publisher_name, "publisher_name")
        course_name = CommonValidators.validate_text_field(course_name, "course_name")
        price = CommonValidators.validate_integer_field(price, "price")
      
      
        if Class not in CLASSES_ARRAY:
            return Response(
                {"error": "فئة الطلاب غير صحيحة"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if subject_name not in SUBJECT_NAMES_ARRAY:
            return Response(
                {"error": "المادة الدراسية غير صحيحة"},
                status=status.HTTP_400_BAD_REQUEST,
            )
         
        if level not in LEVELS_ARRAY:
            return Response(
                {"error": "المستوى الدراسي غير صحيح"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
        if order_by not in ["created_at","price","level","number_of_enrollments","number_of_completions"]:
            return Response(
                {"error": "الترتيب غير صحيح"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        courses = Course.objects.select_related("publisher_id").filter(active=True)

        if publisher_name:
            courses = courses.filter(publisher__full_name_icontains=publisher_name)
        if course_name:
            courses = courses.filter(name_icontains=course_name)
        if Class:
            courses = courses.filter(Class=Class)
        if subject_name:
            courses = courses.filter(subject_name=subject_name)
        if level:
            courses = courses.filter(level=level)
        if price:
            courses = courses.filter(price__lte=price)
        if order_by:
            courses = courses.order_by(order_by)

        begin = count * limit
        if begin > courses.count():
            begin = courses.count()
        end = (count + 1) * limit
        if end > courses.count():
            end = courses.count()

        serializer = CourseListSerializer(courses[begin:end], many=True)

        return Response(
            {"courses": serializer.data, "total_number": courses.count()},
            status=status.HTTP_200_OK,
        )
        
    else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_course_cards_by_publisher_public_id(request, publisher_public_id):

   try:
    limit, count = validate_pagination_parameters(request.data.get("count", 0), request.data.get("limit", 7))

    courses = Course.objects.select_related("publisher_id").filter(active=True, publisher_id__uuid=publisher_public_id)

    begin = count * limit
    if begin > courses.count():
        begin = courses.count()
    end = (count + 1) * limit
    if end > courses.count():
        end = courses.count()

    serializer = CourseListSerializer(courses[begin:end], many=True)

    return Response(
        {"courses": serializer.data, "total_number": courses.count()},
        status=status.HTTP_200_OK,
    )

   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_courses_list_for_dashboard(request):

    publisher_id = request.user.id
    Class = request.query_params.get("Class")
    subject_name = request.query_params.get("subject_name")
    level = request.query_params.get("level")
    price = request.query_params.get("price")
    active = request.query_params.get("active")
    name = request.query_params.get("name")
    order_by = request.query_params.get(
        "order_by"
    )  #price , level ,number_of_enrollments, number_of_completions , number_of_purchases , profit_amount , number_of_lessons,
    count, limit = validate_pagination_parameters(request.query_params.get("count", 0), request.query_params.get("limit", 7))
    
    if active == "true":
        active = True
    elif active == "false":
        active = False
 
    if name and len(name) > 0:
     name = CommonValidators.validate_text_field(name, "name")
    
    if price != "all" and price != None:
     price = CommonValidators.validate_integer_field(price, "price")
 
 
    if Class != "all" and Class not in CLASSES_ARRAY:
        return Response(
            {"error": "صف الطلاب غير صحيح"},
            status=status.HTTP_400_BAD_REQUEST,
        )
 
    if subject_name != "all" and subject_name not in SUBJECT_NAMES_ARRAY:
        return Response(
            {"error": "المادة الدراسية غير صحيحة"},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    if level != "all" and level not in LEVELS_ARRAY:
        return Response(
            {"error": "المستوى الدراسي غير صحيح"},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    if active != "all" and active not in [True, False]:
        return Response(
            {"error": "الحالة غير صحيحة"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    if order_by not in ["price","level","number_of_enrollments","number_of_completions","number_of_purchases","profit_amount","number_of_lessons" ,"created_at" ]:
        return Response(
            {"error": "الترتيب غير صحيح"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    courses = Course.objects.filter(publisher_id=publisher_id)

    if courses.count() <= 0:
        return Response(
            {"courses_list": [], "total_number": 0}, status=status.HTTP_204_NO_CONTENT
        )
    
    if name and len(name) > 0:
        courses = courses.filter(name__icontains=name)
    if Class != "all" and Class:
        courses = courses.filter(Class=Class)
    if subject_name != "all" and subject_name:
        courses = courses.filter(subject_name=subject_name)
    if level != "all" and level:
        courses = courses.filter(level=level)
    if price != "all" and price is not None:
        courses = courses.filter(price__lte=price)
    if active != "all" and active is not None:
        courses = courses.filter(active=active)

    if order_by != "created_at":
        courses = courses.order_by(order_by)

    begin = count * limit
    end = (count + 1) * limit
    
    if begin > courses.count():
        begin = courses.count()
    if end > courses.count():
        end = courses.count()

    serializer = CourseListDashboardSerializer(courses[begin:end], many=True)

    return Response(
        {"courses_list": serializer.data, "total_number": courses.count()},
        status=status.HTTP_200_OK,
    )


@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_course(request, course_public_id):

   try:
    publisher_id = request.user.id
    publisher = get_object_or_404(User, id=publisher_id)
    publisher_type = publisher.account_type  # teacher, team
    publisher_record = None

    if publisher_type == "teacher":
        publisher_record = get_object_or_404(TeacherProfile, user=publisher)
    elif publisher_type == "team":
        publisher_record = get_object_or_404(TeamProfile, user=publisher)
        
    # check if a student has purchased the course , in this case we can't delete the course
    course = get_object_or_404(Course, public_id=course_public_id)
   
    student_premium_content = StudentPremiumContent.objects.filter(
        course_id=course.id, date_of_expiration__gte=timezone.now()
    )

    if student_premium_content.exists():
        return Response(
            {"error": " عذراً لا يمكنك حذف هذه الدورة لأنه تم شراؤها من قبل طلاب"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    course.delete()
    publisher_record.number_of_courses -= 1
    publisher_record.save()

    return Response({"message": "تم حذف الدورة بنجاح"}, status=status.HTTP_200_OK)
   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_course_details_for_dashboard(request, course_public_id):

   try:
   
    publisher_id = request.user.id
    course =Course.objects.select_related("publisher").get(public_id=course_public_id)

    if publisher_id != course.publisher_id:
        return Response(
            {"error": "غير مصرح لك بعرض تفاصيل هذه الدورة"},
            status=status.HTTP_403_FORBIDDEN,
        )
   
    serializer = CourseDetailsForDashboardSerializer(course)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"course_details": serializer.data}, status=status.HTTP_200_OK)
   
   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_course_and_lessons(request, course_public_id):
    
    try:
        course = Course.objects.select_related("publisher").get(public_id=course_public_id)
    
        course_serializer = CourseDetailSerializer(course)
    
        lessons = Lessons.objects.filter(course_id=course.id)
    
        lessons_serializer = GetLessonSerializer(lessons, many=True)
    
        return Response({"course": course_serializer.data, "lessons": lessons_serializer.data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_course_preview_list_by_public_publisher_id(request, public_publisher_id):
    try:
        courses = Course.objects.select_related("publisher_id").filter(publisher_id__uuid=public_publisher_id)
        serializer = CoursePreviewListSerializer(courses, many=True)
        return Response({"courses": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
