
#models : 
from rest_framework.views import APIView
from publisherPlans.models import PublisherPlans as TeacherPlan
from teacherProfile.models import TeacherProfile
from teamProfile.models import TeamProfile
from transactions.models import Transactions
from users.models import User
from purchaseHistory.models import PurchaseHistory
from studentPremiumContent.models import StudentPremiumContent
from studentProfile.models import StudentProfile
from notes.models import Note
from exams.models import Exam
from courses.models import Course
from discountCodes.models import DiscountCodes
from courseStatusTracking.models import CourseStatusTracking
from examAppTracking.models import ExamAppTracking
from noteReadTracking.models import NoteReadTracking
#services : 
from services.notification_management import disable_content_by_admin_notification
from services.transaction_manager import record_transaction

#tasks : 
from notifications.tasks import successful_purchase_notification

# DRF
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
#others
from django.conf import settings
import boto3
from botocore.config import Config
import uuid
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
import os
from django.utils import timezone
from django.db.models import Count, Sum
from collections import defaultdict
from utils.security import SecurityValidator


load_dotenv()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purchase_content(request):

    """
    workflow : 
    1- get the data from the request
    2- get the publisher, student, owner, content records
    3- validate the discount code if any
    4- calculate the final price with the discount if any
    5- record the purchases and transactions (publisher, owner, student)
    6- update the balances of the publisher, owner, student, content (case when publisher is not found, the owner will take the publisher's profit and the owner's profit)
    7- put the purchased content in the student's premium contents list
    8- create a notification for the student of successful purchase
    """
    # getting all the data from the request
    student_id = request.user.id
    publisher_public_id = request.data.get("publisher_public_id")
    # publisher_name = request.data.get("publisher_name")
    content_type = request.data.get("content_type")
    content_public_id = request.data.get("content_public_id")
    discount_code = request.data.get("discount_code")
    
    # Validate discount_code for SQL injection if provided
    # if discount_code is not None:


    # getting the publisher, student, owner, content records
    publisher = User.objects.get(uuid=publisher_public_id)
    student = get_object_or_404(StudentProfile, id=student_id)
    owner = User.objects.get(id=os.getenv("OWNER_ID"))
    
 
    content = _get_content(
        content_type, content_public_id
    )  # may be course / exam / note or None

    if content is None:
        # if the content is not found, return an error response
        return Response(
            {"error": "المحتوى غير موجود"}, status=status.HTTP_400_BAD_REQUEST
        )

    discount_value = 0  #  15000 , 20 
    discount_type = "fixed"  # "fixed" or "percentage"
    discountObject = None  #getting the discount code object
    
    # validate the discount code if any
    if discount_code is not None :
        try:
            discount_code = SecurityValidator.validate_input(
                discount_code, "كود الخصم", check_sql_injection=True, check_xss=True
            )
       
        except ValidationError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
       
        discountObject = _get_discount_object(discount_code , content_type , content_public_id)
   
        if (
            discountObject is not None 
            and discountObject.active
            and discountObject.valid_until >= datetime.now()
            and discountObject.number_of_uses < discountObject.number_of_remaining_uses
        ):
         discount_value = discountObject.discount_value
         discount_type = discountObject.discount_type
         discountObject.number_of_uses += 1
         discountObject.save()


    # calculating the final price of content with the discount if any
    final_price = _get_final_price(content.price, discount_value, discount_type) 
    
    if final_price > student.balance:
        return Response(
            {"error": "الرصيد غير كافي"}, status=status.HTTP_400_BAD_REQUEST
        )

    # calculating the publisher's profit and owner's profit
    publisher_profit_percentage = int(os.getenv("PUBLISER_PROFIT_PERCENTAGE", "70"))
  
    # مقدار الربح للاستاذ
    publisher_profit = round((final_price * publisher_profit_percentage) / 100)
   
    owner_profit = round(final_price - publisher_profit)

    # recording the purchases and transactions
    _record_purchases(
        publisher,
        owner,
        student,
        content,
        content_type,
        publisher_profit,
        owner_profit,
        discount_code,
         str(discount_value)+ "%"if discount_type == "percentage" else str(discount_value),
        final_price,
    )

    # updating the balances of the publisher, owner, student and number of purchases of content
    if publisher is not None:

        publisher.balance += publisher_profit
        publisher.save()

        owner.balance += owner_profit
        owner.save()

    else:
        owner.balance += final_price
        owner.save()

    student.balance -= final_price
    student.save()

    content.number_of_purchases += 1
    content.profit_amount += publisher_profit
    content.save()

    # creating a notification for the student
    content_arabic_name = (
        "اختبار"
        if content_type == "exam"
        else "نوطة" if content_type == "note" else "دورة"
    )

    # put the purchased content in the student's premium contents list

    expiration_date = datetime.now() + timedelta(years=1)
 
    StudentPremiumContent.objects.create(
        student_id=student.id,
        type=content_type,
        exam_id=content.id if content_type == "exam" else None,
        note_id=content.id if content_type == "note" else None,
        course_id=content.id if content_type == "course" else None,
        content_public_id=content.public_id,
        publisher_id=publisher.id,
        date_of_expiration=expiration_date,
    )

    # getting the publisher's full name e.g. "الاستاذ محمد عبد الله" or "فريق النجاح"

    # creating a notification for the student of successful purchase
    
    successful_purchase_notification.delay(student.id, content_type, content_arabic_name, content.id, content.name, final_price, publisher.full_name)


def _get_discount_object(discount_code , content_type, content_public_id):
    
       if content_type == "exam" :
        content = DiscountCodes.objects.select_related('exam_id').get(
            discount_code=discount_code, discount_for=content_type, exam__public_id=content_public_id
        )
        return content
    

       elif content_type == "note" :
        content = DiscountCodes.objects.select_related('note_id'). get(
            discount_code=discount_code, discount_for=content_type, note_id__public_id=content_public_id
        )
        return content
       
       elif content_type == "course" :
        content = DiscountCodes.objects.select_related('course_id').get(
            discount_code=discount_code, discount_for=content_type , course_id__public_id=content_public_id
        )
        return content
    
       else:
        return None
        
def _get_final_discount_value(discount_value, discount_type):

    if discount_type == "fixed":
        return discount_value
    elif discount_type == "percentage":
        return discount_value + "%"


def _get_final_price(price, discount_value, discount_type):


    if discount_value > 0:
        if discount_type == "fixed":
            return round(price - discount_value)
        elif discount_type == "percentage":
            return round(price * (1 - discount_value / 100))


def _get_content(content_type, public_content_id):
    if content_type == "note":
        return get_object_or_404(Note, public_id=public_content_id)
    elif content_type == "exam":
        return get_object_or_404(Exam, public_id=public_content_id)
    elif content_type == "course":
        return get_object_or_404(Course, public_id=public_content_id)
    else:
        return None


def _record_purchases(
    publisher,
    owner,
    student,
    content,
    content_type,
    publisher_profit,
    owner_profit,
    discount_code,
    discount_value,
    final_price,
):

    final_owner_profit = owner_profit
    
    if publisher is not None:
        # record purchase record , content , student , teacher
        PurchaseHistory.objects.create(
            publisher_id=publisher.id,
            publisher_name=publisher.full_name,
            content_type=content_type,
            content_id=content.id,
            content_name=content.name,
            content_class=content.Class,
            content_subject_name=content.subject_name,
            student_id=student.id,
            student_name=student.full_name,
            student_city=student.city,
            student_gender=student.gender,
            student_class=student.Class,
            purchase_date=datetime.now(),
            price=final_price,
            publisher_profit=publisher_profit,
            owner_profit=owner_profit,
            discount_code="-" if discount_code is None else discount_code,
            discount_value="-" if discount_value == 0 else discount_value,
        )
        # record transaction record for the publisher
        record_transaction(publisher, publisher_profit, "purchase" , "completed")
 

    else:

        final_owner_profit += publisher_profit
        pass

    # record transaction record for the owner
    
    record_transaction(owner, final_price, "purchase" , "completed")

    # record transaction record for the student
    record_transaction(student, final_price, "purchase" , "completed")




##############################################################################

@permission_classes([IsAuthenticated])
@api_view(["GET"])
def publisher_most_popular_content_preview(request ):
    """
    Return the top five most purchased pieces of content (exams, courses, notes)
    for the requested publisher. Results are sorted by the number of purchases.
    """
    try:
        user = request.user
        publisher = get_object_or_404(User, id  = user.id)

        limit = 5

        exams_queryset = (
            Exam.objects.filter(publisher_id=publisher, active=True)
            .values("public_id", "name", "number_of_apps", "subject_name", "Class")
        )
        courses_queryset = (
            Course.objects.filter(publisher_id=publisher, active=True)
            .values("public_id", "name", "number_of_enrollments", "subject_name", "Class")
        )
        notes_queryset = (
            Note.objects.filter(publisher_id=publisher, active=True)
            .values("public_id", "name", "number_of_downloads", "subject_name", "Class")
        )
        
        exam_limit = min(limit, len(exams_queryset))
        course_limit = min(limit, len(courses_queryset))
        note_limit = min(limit, len(notes_queryset))
        
        exams_data = [
            {
                "content_type": "exam",
                "public_id": exam["public_id"],
                "name": exam["name"],
                "subject_name": exam["subject_name"],
                "class": exam["Class"],
                "type" : "exam",
                "applications_count": exam["number_of_apps"],
            }
            for exam in exams_queryset[:exam_limit]
        ]

        courses_data = [
            {
                "content_type": "course",
                "public_id": course["public_id"],
                "name": course["name"],
                "subject_name": course["subject_name"],
                "class": course["Class"],
                "type" : "course",
                "applications_count": course["number_of_enrollments"],
            }
            for course in courses_queryset[:course_limit]
        ]

        notes_data = [
            {
                "content_type": "note",
                "public_id": note["public_id"],
                "name": note["name"],
                "subject_name": note["subject_name"],
                "class": note["Class"],
                "type" : "note",
                "applications_count": note["number_of_downloads"],
            }
            for note in notes_queryset[:note_limit]
        ]

        combined_content = exams_data + courses_data + notes_data
        combined_content.sort(key=lambda item: item["applications_count"], reverse=True)
        combined_content_limit = min(limit, len(combined_content))
        return Response(
            {
                "publisher_id": publisher.uuid,
                "results": combined_content[:combined_content_limit],
              
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        print('here  is e' , e)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def publisher_most_purchased_content_preview(request):
    """
    Return the top five most purchased pieces of content (exams, courses, notes)
    for the requested publisher. Results are sorted by the number of purchases.
    """
    try:
        user = request.user
        publisher = get_object_or_404(User, id = user.id)

        limit = 5

        exams_queryset = (
            Exam.objects.filter(publisher_id=publisher, active=True)
            .values("public_id", "name", "number_of_purchases", "subject_name", "Class")
        )
        courses_queryset = (
            Course.objects.filter(publisher_id=publisher, active=True)
            .values("public_id", "name", "number_of_purchases", "subject_name", "Class")
        )
        notes_queryset = (
            Note.objects.filter(publisher_id=publisher, active=True)
            .values("public_id", "name", "number_of_purchases", "subject_name", "Class")
        )
        
        exam_limit = min(limit, len(exams_queryset))
        course_limit = min(limit, len(courses_queryset))
        note_limit = min(limit, len(notes_queryset))
        
        exams_data = [
            {
                "content_type": "exam",
                "public_id": exam["public_id"],
                "name": exam["name"],
                "subject_name": exam["subject_name"],
                "class": exam["Class"],
                "type" : "exam",
                "purchases_count": exam["number_of_purchases"],
            }
            for exam in exams_queryset[:exam_limit]
        ]

        courses_data = [
            {
                "content_type": "course",
                "public_id": course["public_id"],
                "name": course["name"],
                "subject_name": course["subject_name"],
                "class": course["Class"],
                "type" : "course",
                "purchases_count": course["number_of_purchases"],
            }
            for course in courses_queryset[:course_limit]
        ]

        notes_data = [
            {
                "content_type": "note",
                "public_id": note["public_id"],
                "name": note["name"],
                "subject_name": note["subject_name"],
                "class": note["Class"],
                "type" : "note",
                "purchases_count": note["number_of_purchases"],
            }
            for note in notes_queryset[:note_limit]
        ]

        combined_content = exams_data + courses_data + notes_data
        combined_content.sort(key=lambda item: item["purchases_count"], reverse=True)
        combined_content_limit = min(limit, len(combined_content))
        return Response(
            {
                "publisher_id": publisher.uuid,
                "results": combined_content[:combined_content_limit],
              
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def publisher_most_profitable_content_preview(request):
    """
    Return the top five most profitable pieces of content (exams, courses, notes)
    for the requested publisher. Results are sorted by the total profits.
    """
    try:
        user = request.user
        publisher = get_object_or_404(User, id = user.id)

        limit = 5

        exams_queryset = (
            Exam.objects.filter(publisher_id=publisher, active=True)
            .values("public_id", "name", "profit_amount", "subject_name", "Class")
        )
        courses_queryset = (
            Course.objects.filter(publisher_id=publisher, active=True)
            .values("public_id", "name", "profit_amount", "subject_name", "Class")
        )
        notes_queryset = (
            Note.objects.filter(publisher_id=publisher, active=True)
            .values("public_id", "name", "profit_amount", "subject_name", "Class")
        )
        
        exam_limit = min(limit, len(exams_queryset))
        course_limit = min(limit, len(courses_queryset))
        note_limit = min(limit, len(notes_queryset))
        
        exams_data = [
            {
                "content_type": "exam",
                "public_id": exam["public_id"],
                "name": exam["name"],
                "subject_name": exam["subject_name"],
                "class": exam["Class"],
                "type" : "exam",
                "profit_amount": exam["profit_amount"],
            }
            for exam in exams_queryset[:exam_limit]
        ]

        courses_data = [
            {
                "content_type": "course",
                "public_id": course["public_id"],
                "name": course["name"],
                "subject_name": course["subject_name"],
                "class": course["Class"],
                "type" : "course",
                "profit_amount": course["profit_amount"],
            }
            for course in courses_queryset[:course_limit]
        ]

        notes_data = [
            {
                "content_type": "note",
                "public_id": note["public_id"],
                "name": note["name"],
                "subject_name": note["subject_name"],
                "class": note["Class"],
                "type" : "note",
                "profit_amount": note["profit_amount"],
            }
            for note in notes_queryset[:note_limit]
        ]

        combined_content = exams_data + courses_data + notes_data
        combined_content.sort(key=lambda item: item["profit_amount"], reverse=True)
        combined_content_limit = min(limit, len(combined_content))
        return Response(
            {
                "publisher_id": publisher.uuid,
                "results": combined_content[:combined_content_limit],
              
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def publisher_student_analysis_last_month_date(request ):
    """
    Aggregate the last month's student activity grouped by last date activity across
    courses, exams, and notes for the requested publisher.
    last date activity is the last date the student accessed the content. ( last date record has been updated )
    """
    try:
        user = request.user 
        publisher = get_object_or_404(User, id = user.id)
        current_time = timezone.now()
        start_date = current_time - timedelta(days=30)
        
        # Generate all dates in the range [current_date - 30 days, current_date]
        current_date = timezone.localtime(current_time).date()
        start_date_only = start_date.date() if isinstance(start_date, datetime) else start_date
        
        # Initialize date_stats with all dates in the range, set to 0
        date_stats = {}
        for i in range(31):  # 30 days + current day = 31 days
            date_key = (start_date_only + timedelta(days=i)).isoformat()
            date_stats[date_key] = {
                "date": date_key,
                "total": 0,
                "courses": 0,
                "exams": 0,
                "notes": 0
            }

        def _bump_date(date_value, field, count):
            if isinstance(date_value, datetime):
                if timezone.is_aware(date_value):
                    date_key = timezone.localtime(date_value).date().isoformat()
                else:
                    date_key = date_value.date().isoformat()
            elif isinstance(date_value, date):
                date_key = date_value.isoformat()
            else:
                date_key = "unknown"
            
            # Only update if the date is in our range
            if date_key in date_stats:
                record = date_stats[date_key]
                record[field] += count
                record["total"] += count

        course_counts = (
            CourseStatusTracking.objects.filter(
                publisher_id=publisher,
                student_id__isnull=False,
                created_at__gte=start_date,
            )
            .values("updated_at")
            .annotate(total=Count("id"))
        )

        for course in course_counts:
            _bump_date(course["updated_at"], "courses", course["total"])

        exam_counts = (
            ExamAppTracking.objects.filter(
                publisher_id=publisher,
                created_at__gte=start_date,
            )
            .values("updated_at")
            .annotate(total=Count("id"))
        )

        for exam in exam_counts:
            _bump_date(exam["updated_at"], "exams", exam["total"])

        note_counts = (
            NoteReadTracking.objects.filter(
                publisher_id=publisher,
                student_id__isnull=False,
                created_at__gte=start_date,
            )
            .values("updated_at")
            .annotate(total=Count("id"))
        )

        for note in note_counts:
            _bump_date(note["updated_at"], "notes", note["total"])
            
        date_distribution = sorted(
            date_stats.values(), key=lambda item: item["date"], reverse=True
        )

        return Response(
            {
                "publisher_id": str(publisher.uuid),
                "date_distribution": date_distribution,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def publisher_student_analysis_last_month_city(request ):
    """
    Aggregate the last month's student activity grouped by city for the requested publisher.
    """
    try:
        user = request.user 
        publisher = get_object_or_404(User, id = user.id)
        current_time = timezone.now()
        start_date = current_time - timedelta(days=30)

        city_stats = defaultdict(
            lambda: {"city": "unknown", "total": 0, "courses": 0, "exams": 0, "notes": 0}
        )
        
        def _bump_city(city_value, field, count):
            city_key = city_value or "unknown"
            record = city_stats[city_key]
            record["city"] = city_key
            record[field] += count
            record["total"] += count

        course_counts = (
            CourseStatusTracking.objects.filter(
                publisher_id=publisher,
                student_id__isnull=False,
                created_at__gte=start_date,
            )
            .values("student_id__city")
            .annotate(total=Count("id"))
        )

        for course in course_counts:
            _bump_city(course["student_id__city"], "courses", course["total"])

        exam_counts = (
            ExamAppTracking.objects.filter(
                publisher_id=publisher,
                created_at__gte=start_date,
            )
            .values("student_id__city")
            .annotate(total=Count("id"))
        )

        for exam in exam_counts:
            _bump_city(exam["student_id__city"], "exams", exam["total"])

        note_counts = (
            NoteReadTracking.objects.filter(
                publisher_id=publisher,
                student_id__isnull=False,
                created_at__gte=start_date,
            )
            .values("student_id__city")
            .annotate(total=Count("id"))
        )

        for note in note_counts:
            _bump_city(note["student_id__city"], "notes", note["total"])
            
        city_distribution = sorted(
            city_stats.values(), key=lambda item: item["total"], reverse=True
        )

        return Response(
            {
                "publisher_id": str(publisher.uuid),
                "city_distribution": city_distribution,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def publisher_student_analysis_last_month_gender(request ):
    """
    Aggregate the last month's student activity grouped by gender for the requested publisher.
    """
    try:
        user = request.user 
        publisher = get_object_or_404(User, id = user.id)
        current_time = timezone.now()
        start_date = current_time - timedelta(days=30)

        
        gender_stats = defaultdict(
            lambda: {"gender": "unknown", "total": 0, "courses": 0, "exams": 0, "notes": 0}
        )
        
        def _bump_gender(gender_value, field, count):
            gender_key = gender_value or "unknown"
            record = gender_stats[gender_key]
            record["gender"] = gender_key
            record[field] += count
            record["total"] += count



        course_counts = (
            CourseStatusTracking.objects.filter(
                publisher_id=publisher,
                student_id__isnull=False,
                created_at__gte=start_date,
            )
            .values("student_id__gender")
            .annotate(total=Count("id"))
        )

        for course in course_counts:
            _bump_gender(course["student_id__gender"], "courses", course["total"])

        exam_counts = (
            ExamAppTracking.objects.filter(
                publisher_id=publisher,
                created_at__gte=start_date,
            )
            .values("student_id__gender")
            .annotate(total=Count("id"))
        )

        for exam in exam_counts:
            _bump_gender(exam["student_id__gender"], "exams", exam["total"])

        note_counts = (
            NoteReadTracking.objects.filter(
                publisher_id=publisher,
                student_id__isnull=False,
                created_at__gte=start_date,
            )
            .values("student_id__gender")
            .annotate(total=Count("id"))
        )

        for note in note_counts:
            _bump_gender(note["student_id__gender"], "notes", note["total"])
            
        gender_distribution = sorted(
            gender_stats.values(), key=lambda item: item["total"], reverse=True
        )

        return Response(
            {
                "publisher_id": str(publisher.uuid),
                "gender_distribution": gender_distribution,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
 
@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def disable_exam(request , exam_public_id):
    """
    Disable an exam
    """
    try: 
        
        publisher_id =   request.user.id
        user = get_object_or_404(User, id=publisher_id)
        publisher_type = user.account_type #teacher, team
        disabled_by = request.data.get("disabled_by" , "publisher") #publisher, admin
        
        publisher = None
        if publisher_type == "teacher":
            publisher = get_object_or_404(TeacherProfile, id=publisher_id)
        elif publisher_type == "team":
            publisher = get_object_or_404(TeamProfile, id=publisher_id)

        exam = get_object_or_404(Exam, public_id=exam_public_id)
        
        if exam.active:
            exam.active = False
            exam.disable_date = timezone.now()
            exam.disabled_by = disabled_by
            publisher.number_of_exams -= 1
        else : 
            exam.disabled_by = disabled_by

        if exam.disabled_by == "admin":           
         disable_content_by_admin_notification(publisher_id, "exam", exam.id, exam.name)
        exam.save()
        publisher.save()
        

        return Response({"message": "تم تعطيل الامتحان بنجاح"},status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )
        
    
@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def activate_exam(request , exam_public_id):
    
   try:
    publisher_id = request.user.id
    user = get_object_or_404(User, id=publisher_id)
    publisher_type = user.account_type #teacher, team
    activated_by = request.data.get("activated_by" , "publisher") #publisher, admin
    
    exam = get_object_or_404(Exam, public_id=exam_public_id)
   
    if exam.active:
        return Response({"error": "الامتحان مفعل بالفعل"}, status=status.HTTP_400_BAD_REQUEST)
   
    publisher = None
   
    if publisher_type == "teacher":
        publisher = get_object_or_404(TeacherProfile, id=publisher_id)
    elif publisher_type == "team":
        publisher = get_object_or_404(TeamProfile, id=publisher_id)
    
    currentPublisherPlan = TeacherPlan.objects.get(user=publisher.user)
    
    if  exam.disabled_by == "admin"  and activated_by != "admin": 
        return Response({"error": "لا يمكنك تفعيل الامتحان لانه تم تعطيله من قبل إدارة المنصة"}, status=status.HTTP_400_BAD_REQUEST)
    
    if publisher.number_of_exams + 1 > currentPublisherPlan.number_of_allowed_exams:
        return Response({"error": "تم تجاوز الحد المسموح به للاختبارات"}, status=status.HTTP_400_BAD_REQUEST)
   
    exam.active = True
    exam.save()
    
    publisher.number_of_exams += 1
    publisher.save()
    
    return Response({"message": "تم تفعيل الامتحان بنجاح"},status=status.HTTP_200_OK)
   
   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
     
     
@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def disable_note(request , note_public_id):
    """
    Disable a note
    """
    try: 
        
        publisher_id =   request.user.id
        user = get_object_or_404(User, id=publisher_id)
        publisher_type = user.account_type #teacher, team
        disabled_by = request.data.get("disabled_by" , "publisher") #publisher, admin
        
        publisher = None
        if publisher_type == "teacher":
            publisher = get_object_or_404(TeacherProfile, id=publisher_id)
        elif publisher_type == "team":
            publisher = get_object_or_404(TeamProfile, id=publisher_id)

        note = get_object_or_404(Note, public_id=note_public_id)

        if note.active:
            note.active = False
            note.disable_date = timezone.now()
            note.disabled_by = disabled_by
            publisher.number_of_notes -= 1
        else : 
            note.disabled_by = disabled_by
            
        if note.disabled_by == "admin":           
         disable_content_by_admin_notification(publisher_id, "note", note.id, note.name)
        note.save()
        publisher.save()

        return Response({"message": "تم تعطيل النوطة بنجاح"},status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": "النوطة غير موجودة"}, status=status.HTTP_404_NOT_FOUND
        )
     

@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def activate_note(request , note_public_id):
   try:
    publisher_id = request.user.id
    user = get_object_or_404(User, id=publisher_id)
    publisher_type = user.account_type #teacher, team
    activated_by = request.data.get("activated_by" , "publisher") #publisher, admin
    
    
    note = get_object_or_404(Note, public_id=note_public_id)

    if note.active:
        return Response({"error": "النوطة مفعلة بالفعل"}, status=status.HTTP_400_BAD_REQUEST)

    if note.disabled_by == "admin"  and activated_by != "admin": 
        return Response({"error": "لا يمكنك تفعيل النوطة لانه تم تعطيلها من قبل إدارة المنصة"}, status=status.HTTP_400_BAD_REQUEST)

    publisher = None

    if publisher_type == "teacher":
        publisher = get_object_or_404(TeacherProfile, id=publisher_id)
    elif publisher_type == "team":
        publisher = get_object_or_404(TeamProfile, id=publisher_id)
    
    currentPublisherPlan = TeacherPlan.objects.get(user=publisher.user)
    
    if publisher.number_of_notes + 1 > currentPublisherPlan.number_of_allowed_notes:
        return Response({"error": "تم تجاوز الحد المسموح به للنوطات"}, status=status.HTTP_400_BAD_REQUEST)

    note.active = True
    note.save()
    
    publisher.number_of_notes += 1
    publisher.save()
    
    return Response({"message": "تم تفعيل النوطة بنجاح"},status=status.HTTP_200_OK)
   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


   
@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def disable_course(request , course_public_id):
    """
    Disable a course
    """
    try: 
        
        publisher_id =   request.user.id
        user = get_object_or_404(User, id=publisher_id)
        publisher_type = user.account_type #teacher, team
        disabled_by = request.data.get("disabled_by" , "publisher") #publisher, admin
        
        publisher = None
        if publisher_type == "teacher":
            publisher = get_object_or_404(TeacherProfile, id=publisher_id)
        elif publisher_type == "team":
            publisher = get_object_or_404(TeamProfile, id=publisher_id)

        course = get_object_or_404(Course, public_id=course_public_id)

        if course.active:
            course.active = False
            course.disable_date = timezone.now()
            course.disabled_by = disabled_by
            publisher.number_of_courses -= 1
        else : 
            course.disabled_by = disabled_by
            
        if course.disabled_by == "admin":           
         disable_content_by_admin_notification(publisher_id, "course", course.id, course.name)
        course.save()
        publisher.save()
        #if course is disabled by admin , then send notification to the publisher
        return Response({"message": "تم تعطيل الدورة بنجاح"},status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    
@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def activate_course(request , course_public_id):
   
   try:
    publisher_id = request.user.id
    user = get_object_or_404(User, id=publisher_id)
    publisher_type = user.account_type #teacher, team
    activated_by = request.data.get("activated_by" , "publisher") #publisher, admin
    course = get_object_or_404(Course, public_id=course_public_id)
    
    if course.active:
        return Response({"error": "الدورة مفعلة بالفعل"}, status=status.HTTP_400_BAD_REQUEST)
    
    if course.disabled_by == "admin"  and activated_by != "admin": 
        return Response({"error": "لا يمكنك تفعيل الدورة لانه تم تعطيلها من قبل إدارة المنصة"}, status=status.HTTP_400_BAD_REQUEST)
    
    publisher = None
    
    if publisher_type == "teacher":
        publisher = get_object_or_404(TeacherProfile, id=publisher_id)
    elif publisher_type == "team":
        publisher = get_object_or_404(TeamProfile, id=publisher_id)
    
    currentPublisherPlan = TeacherPlan.objects.get(user=publisher.user)
    
    if publisher.number_of_courses + 1 > currentPublisherPlan.number_of_allowed_courses:
        return Response({"error": "تم تجاوز الحد المسموح به للدورات"}, status=status.HTTP_400_BAD_REQUEST)
    
    course.active = True
    course.save()
    
    publisher.number_of_courses += 1
    publisher.save()
    
    return Response({"message": "تم تفعيل الدورة بنجاح"},status=status.HTTP_200_OK)
   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def platform_statistics(request):
    """
    Return platform statistics including total counts of exams, notes, courses,
    students, publishers, and total profit from purchase history.
    """
    try:
        # Count content
        total_exams = Exam.objects.count()
        total_notes = Note.objects.count()
        total_courses = Course.objects.count()
        
        # Count users by account type
        total_users = User.objects.count()
        total_students = User.objects.filter(account_type="student").count()
        total_publishers = total_users - total_students - 1
        
        
        # Calculate total profit from purchase history
        profit_aggregate = PurchaseHistory.objects.aggregate(
            total_publisher_profit=Sum("publisher_profit"),
            total_owner_profit=Sum("owner_profit"),
        )
        total_profit = (profit_aggregate["total_publisher_profit"] or 0) + (
            profit_aggregate["total_owner_profit"] or 0
        )
        
        return Response(
            {
                "total_exams": total_exams,
                "total_notes": total_notes,
                "total_courses": total_courses,
                "total_students": total_students,
                "total_publishers": total_publishers,
                "total_profit": str(total_profit),
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def publisher_statistics(request):
    """
    Return publisher statistics including total counts of exams, notes, courses,
    students, publishers, and total profit from purchase history.
    """
    try:
       user = request.user
       user = get_object_or_404(User, id=user.id)
       publisher_type = user.account_type #teacher, team
       publisher = None
       if publisher_type == "teacher":
           publisher = get_object_or_404(TeacherProfile, user=user.id)
       elif publisher_type == "team":
           publisher = get_object_or_404(TeamProfile, user=user.id)
       return Response({
        "number_of_exams": publisher.number_of_exams,
        "number_of_notes": publisher.number_of_notes,
        "number_of_courses": publisher.number_of_courses,
        "number_of_followers": publisher.number_of_followers,
       },status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


 

class PresignedURLView(APIView):
    permission_classes([IsAuthenticated])
    def post(self, request):
        """
        Generate presigned URL for direct upload to Backblaze B2
        """
        file_name = request.data.get('file_name')
        file_type = request.data.get('file_type', 'application/octet-stream')
        file_size = request.data.get('file_size')

        if not file_name:
            return Response(
                {'error': 'file_name is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique file key
        file_extension = file_name.split('.')[-1] if '.' in file_name else 'bin'
        unique_id = uuid.uuid4()
        file_key = f"uploads/{unique_id}.{file_extension}"

        # Initialize Backblaze S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_ENDPOINT_URL,  # Your Backblaze endpoint
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,  # Your keyID
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,  # Your applicationKey
            config=Config(signature_version='s3v4')
        )

        try:
            # Generate presigned URL for PUT operation
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.AWS_BUCKET_NAME,
                    'Key': file_key,
                    'ContentType': file_type,
                    # Optional: Add content length restriction for security
                    # 'ContentLength': file_size,
                },
                ExpiresIn=10000,  # URL expires in about 3 hours
                HttpMethod='PUT'
            )

            # Construct the final public URL
            final_url = f"https://your-bucket-name.s3.your-backblaze-region.backblazeb2.com/{file_key}"

            return Response({
                'presigned_url': presigned_url,
                'file_key': file_key,
                'final_url': final_url
            })

        except Exception as e:
            return Response(
                {'error': f'Failed to generate presigned URL: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )