from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status

from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Avg
import fitz  # PyMuPDF
import openai
from openai import OpenAI
from django.conf import settings
import os
import tempfile
import json
# tasks
from notifications.tasks import publishing_exam_notification
from utils.validators import CommonValidators

# models
from .models import Exam
from teacherProfile.models import TeacherProfile
from teamProfile.models import TeamProfile
from studentPremiumContent.models import StudentPremiumContent
from examAppTracking.models import ExamAppTracking
from MCQ.models import MCQ
from users.models import User
from units.models import Unit

# serializers
from MCQ.serializers import MCQSerializer
from .serializers import (
    ExamCardsSerializer,
    ExamCreateSerializer,
    ExamDetailsForDashboardSerializer,
    ExamDetailsSerializer,
    ExamListDashboardSerializer,
    ExamPreviewListSerializer,
    ExamUpdateSerializer,
)

# services
from services.publisher_plan_check import (
    check_publisher_plan,
    check_publishing_content_availability,
)

from services.parameters_validator import validate_pagination_parameters

from Constants import CLASSES_ARRAY , SUBJECT_NAMES_ARRAY , LEVELS_ARRAY

@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def increase_number_of_purchases(request, exam_public_id):
    try:
        exam = get_object_or_404(Exam, public_id=exam_public_id)
        exam.number_of_purchases += 1
        exam.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def change_number_of_comments(request, exam_public_id):
    try:
        number = request.data.get("number", 1)
        exam = get_object_or_404(Exam, public_id=exam_public_id)
        exam.number_of_comments += number
        exam.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def change_exam_metrics(
    request, exam_public_id
):  # change average result , number of apps
    try:
        result = request.data.get("result")
        result = float(result)
        exam = get_object_or_404(Exam, public_id=exam_public_id)

        exam.result_avg = round((result + exam.result_avg) / 2, 2)
        exam.number_of_apps += 1
        exam.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_exam(request):
    try:
        user = get_object_or_404(User, id=request.user.id)
        publisher_id = user.id
        publisher_type = user.account_type
        
        if publisher_type != "teacher" and publisher_type != "team" :
            return Response(
                 "غير مصرح لك بإنشاء اختبار",
                status=status.HTTP_403_FORBIDDEN,
            )
        if not check_publishing_content_availability(   
            publisher_id, publisher_type, "exam"
        ):
            return Response(
                "لقد تجاوزت الحد المسموح به لنشر الاختبارات",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Add publisher_id to the data
        data = request.data.copy()
        data['publisher_id'] = publisher_id
        
        mcqs_data = request.data.get('questions', [])
        if not mcqs_data:
            return Response(
                "يجب أن يكون لديك سؤال واحد على الأقل",
                status=status.HTTP_400_BAD_REQUEST
            )
        data['number_of_questions'] = len(mcqs_data) if isinstance(mcqs_data, list) else 0
     
        serializer = ExamCreateSerializer(data=data)

        if serializer.is_valid():
            exam = serializer.save()
            
            # Handle units many-to-many relationship
            unit_public_ids = request.data.get('unit', [])
            if unit_public_ids:
                if not isinstance(unit_public_ids, list):
                    return Response(
                        "يجب أن تكون الوحدات مصفوفة",
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get Unit objects by public_id
                units = Unit.objects.filter(public_id__in=unit_public_ids)
                found_public_ids = set(units.values_list('public_id', flat=True))
                missing_public_ids = set(unit_public_ids) - found_public_ids
                
                if missing_public_ids:
                    return Response(
                        f"الوحدات التالية غير موجودة: {', '.join(missing_public_ids)}",
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Associate units with exam
                exam.units.set(units)
            
            # Create MCQs if provided
  
            if mcqs_data:
                for mcq_data in mcqs_data:
                    mcq_data_copy = mcq_data.copy()
                    mcq_data_copy['exam'] = exam.id
                    mcq_serializer = MCQSerializer(data=mcq_data_copy)
                    if mcq_serializer.is_valid():
                        mcq_serializer.save()
                    else:
                        # If MCQ validation fails, return error
                        return Response(
                           f"خطأ في إنشاء السؤال: {mcq_serializer.errors}",
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            # publishing_exam_notification.delay(exam.id, user)
            profile = None
            if publisher_type == "teacher":
                profile = get_object_or_404(TeacherProfile, user=user)
            elif publisher_type == "team":
                profile = get_object_or_404(TeamProfile, user=user)
            profile.number_of_exams += 1
            profile.save()
            return Response(
                {
                    "message": "تم إنشاء الاختبار بنجاح",
                    "exam_public_id": exam.public_id,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response( str(e), status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH", "PUT"])
def update_exam(request, exam_public_id):
    try:
        publisher_id = request.user.id
        exam = get_object_or_404(Exam, public_id=exam_public_id)

        if exam.publisher_id != publisher_id:
            return Response(
                {"error": "غير مصرح لك بتحديث هذا الامتحان"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Pass the instance to the serializer for update
        serializer = ExamUpdateSerializer(exam, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_exam_details(request, exam_public_id):
    try:
        source = request.data.get("source")  # purchase | course | public
        exam = get_object_or_404(Exam, public_id=exam_public_id)

        check_publisher_plan(exam.publisher_id)

        # here after we check the plan, we get the exam again to make sure it is still active
        exam = Exam.objects.select_related("publisher_id").get(public_id=exam_public_id)
        user = get_object_or_404(User, id=request.user.id)

        serializer = ExamDetailsSerializer(exam)

        if not serializer.data["active"]:
            if source == "public":
                return Response(
                    {"error": "عذراً هذا الامتحان لم يعد متوفر"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if source == "public" and exam.visibility != "public":
            return Response(
                {"error": "عذراً هذا الاختبار غير متوفر للعرض بشكل عام"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        has_entered_before = ExamAppTracking.objects.filter(
            exam_id=exam,
            student_id=user,
        ).exists()

        is_purchased_before = True

        if exam.price and exam.price > 0:
            student_premium_content = StudentPremiumContent.objects.get(
                exam_id=exam, student_id=user
            )

            if (
                student_premium_content
                and student_premium_content.date_of_expiration < timezone.now()
            ):
                is_purchased_before = False
                student_premium_content.delete()

        return Response(
            {
                "exam_details": serializer.data,
                "is_purchased_before": is_purchased_before,
                "has_entered_before": has_entered_before,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_exam_cards(request):
    try:
        publisher_name = request.data.get("publisher_name")
        exam_name = request.data.get("exam_name")
        Class = request.data.get("Class")
        subject_name = request.data.get("subject_name")
        units = request.data.get("units")
        level = request.data.get("level")
        price = request.data.get("price")
        result_avg = request.data.get("result_avg")
        order_by = request.data.get(
            "order_by"
        )  # result_avg , created_at , level ,price , number_of_questions, number_of_apps, number_of_likes

        limit, count = validate_pagination_parameters(request.data.get("count", 0), request.data.get("limit", 7))
        publisher_name = CommonValidators.validate_text_field(publisher_name, "publisher_name")
        exam_name = CommonValidators.validate_text_field(exam_name, "exam_name")
        result_avg = CommonValidators.validate_float_field(result_avg, "result_avg")
       
        if order_by not in ["result_avg" , "created_at" , "level" , "price" , "number_of_questions" , "number_of_apps" ]:
            return Response(
                {"error": "الترتيب غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Class not in CLASSES_ARRAY:
            return Response(
                {"error": "الصف غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if subject_name not in SUBJECT_NAMES_ARRAY:
            return Response(
                {"error": "المادة غير متوفرة"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if level not in LEVELS_ARRAY:
            return Response(
                {"error": "المستوى غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
      
      
      
        exams = Exam.objects.select_related("publisher_id").filter(
            active=True, visibility="public"
        ).order_by("-created_at")
        

        if publisher_name:
            exams = exams.filter(publisher_id__full_name__icontains=publisher_name)
        if exam_name:
            exams = exams.filter(name__icontains=exam_name)
        if Class:
            exams = exams.filter(Class=Class)
        if subject_name:
            exams = exams.filter(subject_name=subject_name)
        if units:
            exams = exams.filter(units__icontains=units)
        if level:
            exams = exams.filter(level=level)
        if price:
            exams = exams.filter(price__lte=price)
        if result_avg:
            exams = exams.filter(result_avg__gte=result_avg)
        if order_by:
            exams = exams.order_by(order_by)

        begin = count * limit
        if begin > exams.count():
            begin = exams.count()
        end = (count + 1) * limit
        if end > exams.count():
            end = exams.count()

        serializer = ExamCardsSerializer(exams[begin:end], many=True)

        return Response(
            {"exam_cards": serializer.data, "total_number": exams.count()},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_exam_cards_by_publisher_public_id(request, publisher_public_id):
    try:
        count, limit = validate_pagination_parameters(request.query_params.get("count", 0), request.query_params.get("limit", 7))

        exams = Exam.objects.select_related("publisher_id").filter(
            active=True, visibility="public", publisher_id__uuid=publisher_public_id
        ).order_by("-created_at")

        begin = count * limit
        
        if begin > exams.count():
            begin = exams.count()
            
        end = (count + 1) * limit
        
        if end > exams.count():
            end = exams.count()

        serializer = ExamCardsSerializer(exams[begin:end], many=True)

        return Response(
            {"exam_cards": serializer.data, "total_number": exams.count()},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_exams_list_for_dashboard(request):
    try:
        publisher_id = request.user.id
        Class = request.query_params.get("Class")
        subject_name = request.query_params.get("subject_name")
        level = request.query_params.get("level")
        price = request.query_params.get("price")
        active = request.query_params.get("active")
        name = request.query_params.get("name")
        order_by = request.query_params.get(
            "order_by"
        )  
        count,limit = validate_pagination_parameters(request.query_params.get("count", 0), request.query_params.get("limit", 7))
         
        if name and len(name) > 0:
         name = CommonValidators.validate_text_field(name, "name")
       
        if order_by not in ["result_avg" , "created_at" , "level" , "price" , "number_of_questions" , "number_of_apps" , "profit_amount" , "number_of_purchases" ]:
            return Response(
                {"error": "الترتيب غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
            
        if Class != "all" and Class not in CLASSES_ARRAY:
            return Response(
                {"error": "الصف غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Class = CommonValidators.validate_text_field(Class, "Class")
        
        
        if subject_name != "all" and subject_name not in SUBJECT_NAMES_ARRAY:
            return Response(
                {"error": "المادة غير متوفرة"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subject_name = CommonValidators.validate_text_field(subject_name, "subject_name")
        
        if level != "all" and level  not in LEVELS_ARRAY:
            return Response(
                {"error": "المستوى غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        level = CommonValidators.validate_text_field(level, "level")
        
        if active == "true":
            active = True
        elif active == "false":
            active = False
        if active != "all" and active not in [True, False]:
            return Response(
                {"error": "الحالة غير متوفرة"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if price != "all":
            price = CommonValidators.validate_money_amount(price , "السعر")
        
        exams = Exam.objects.filter(publisher_id=publisher_id).order_by("-created_at")

        if exams.count() <= 0:
            return Response(
                {"exams_list": [], "total_number": 0}, status=status.HTTP_204_NO_CONTENT
            )
        if name and len(name) > 0:
            exams = exams.filter(name__icontains=name)
        if Class != "all" and Class:
            exams = exams.filter(Class=Class)
        if subject_name != "all" and subject_name:
            exams = exams.filter(subject_name=subject_name)
        if level != "all" and level:
            exams = exams.filter(level=level)
        if price!= "all" and price is not None:
            exams = exams.filter(price__lte=price)
        if active != "all" and active is not None:
            exams = exams.filter(active=active)

        if order_by != "created_at":
            exams = exams.order_by(order_by)

        begin = count * limit
        if begin > exams.count():
            begin = exams.count()
            
        end = (count + 1) * limit
        if end > exams.count():
            end = exams.count()

        serializer = ExamListDashboardSerializer(exams[begin:end], many=True)

        return Response(
            {"exams_list": serializer.data, "total_number": exams.count()},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_average_results_for_all_exams_by_publisher_id(request):
    try:
        publisher_id = request.user.id
        exams = Exam.objects.filter(publisher_id=publisher_id)

        easy_average_result = (
            exams.filter(level="سهل").aggregate(Avg("result_avg"))["result_avg__avg"]
            or 0
        )
        medium_average_result = (
            exams.filter(level="متوسط").aggregate(Avg("result_avg"))["result_avg__avg"]
            or 0
        )
        hard_average_result = (
            exams.filter(level="صعب").aggregate(Avg("result_avg"))["result_avg__avg"]
            or 0
        )

        total_count = exams.count()
        if total_count > 0:
            average_results = (
                easy_average_result + medium_average_result + hard_average_result
            ) / 3
        else:
            average_results = 0

        return Response(
            {
                "avg": round(average_results, 2),
                "easy_avg": round(easy_average_result, 2),
                "medium_avg": round(medium_average_result, 2),
                "hard_avg": round(hard_average_result, 2),
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_exam(request, exam_public_id):
    try:
        publisher_id = request.user.id
        publisher = get_object_or_404(User, id=publisher_id)
        publisher_type = publisher.account_type
        publisher_record = None

        if publisher_type not in ["teacher", "team" , "admin"]:
            return Response(
                {"error": "النوع غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if publisher_type == "teacher":
            publisher_record = get_object_or_404(TeacherProfile, user=publisher)
        elif publisher_type == "team":
            publisher_record = get_object_or_404(TeamProfile, user=publisher)

        exam = get_object_or_404(Exam, public_id=exam_public_id)

        # check if a student has purchased the exam, in this case we can't delete the exam
        student_premium_content = StudentPremiumContent.objects.filter(
            exam_id=exam.id, date_of_expiration__gte=timezone.now()
        )

        if student_premium_content.exists():
            return Response(
                {"error": " عذراً لا يمكنك حذف هذا الامتحان لأنه تم شراؤه من قبل طلاب"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exam.delete()
        publisher_record.number_of_exams -= 1
        publisher_record.save()

        return Response({"message": "تم حذف الامتحان بنجاح"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_exam_details_for_dashboard(request, exam_public_id):
    try:
        publisher_id = request.user
        exam = Exam.objects.select_related("publisher_id").get(public_id=exam_public_id)

        if publisher_id != exam.publisher_id:
            return Response(
                {"error": "غير مصرح لك بعرض تفاصيل هذا الامتحان"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ExamDetailsForDashboardSerializer(exam)
        return Response({"exam_details": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_exam_and_mcqs(request, exam_public_id):
    try:
        exam = Exam.objects.select_related("publisher_id").get(public_id=exam_public_id)
        exam_serializer = ExamDetailsSerializer(exam)
        mcqs = MCQ.objects.filter(exam_id=exam.id).order_by("-created_at")
        mcqs_serializer = MCQSerializer(mcqs, many=True)
        return Response(
            {"exam": exam_serializer.data, "mcqs": mcqs_serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Configure OpenAI client for DeepSeek
client = openai.OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"  # DeepSeek API endpoint
)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_exam_preview_list(request):
    try:
        user = request.user 
        publisher = get_object_or_404(User, id=user.id);
        exams = Exam.objects.select_related("publisher_id").filter(
            publisher_id=publisher.id , price__gt = 0
        )
        serializer = ExamPreviewListSerializer(exams, many=True)
        return Response({"exams": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@permission_classes([IsAuthenticated])
@api_view(['POST'])
def auto_generate_exam_mcqs(request):
    """
    Endpoint to receive extracted text and return generated MCQs.
    
    Expected JSON request format:
    {
        "text": "Extracted text from PDF...",
        "num_questions": 5,
    }
    
    Returns:
    - JSON with generated MCQs and metadata
    """
    try:
        # Parse JSON request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON format in request body.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate required fields
        text = data.get('text', '').strip()
        if not text:
            return Response(
                {'error': 'No text provided. Please provide extracted text.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
 
        # Get optional parameters with defaults
        num_questions = int(data.get('num_questions', 5))
 
        # Validate parameters
        if num_questions < 1 or num_questions > 50:
            return Response(
                {'error': 'Number of questions must be between 1 and 50.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate MCQs using DeepSeek API
        mcqs =generate_mcqs_with_deepseek(text, num_questions)
        
        # Prepare response
        response_data = {
            'success': True,
            'metadata': {
                'text_length': len(text),
                'num_questions_generated': len(mcqs),
                'num_questions_requested': num_questions,
            },
            'questions': mcqs
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate MCQs: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def generate_mcqs_with_deepseek(text, num_questions):
    """
    Generate MCQs using DeepSeek API from provided text.
    
    Args:
        text: Extracted text from PDF
        num_questions: Number of questions to generate

        
    Returns:
        List of MCQ dictionaries
    """
    try:
        # Prepare the prompt with enhanced instructions

        
        prompt = f"""Generate {num_questions} multiple-choice questions based on the following text.
        
        IMPORTANT: Return ONLY valid JSON with this EXACT structure:
        {{
            "questions": [
                {{
                    "q": "Clear and concise question text?",
                    "options": {{
                        "A": "Option A",
                        "B": "Option B", 
                        "C": "Option C",
                        "D": "Option D "
                    }},
                    "ans": "A",
                    "exp": "Detailed explanation why this is correct",
                }}
            ]
        }}
        
        Text content:
        {text[:30000]}  # Limit text to avoid token limits
        
        Guidelines:
        1. Questions must test comprehension of key concepts in the text
        2. Each question must have exactly 4 distinct, plausible options
        3. Only one correct answer per question
        4. Vary question types as specified
        5. Ensure questions cover different parts of the text
        6. Return ONLY the JSON object, no other text or markdown
        7. Questions should be in Arabic if the text is in Arabic, otherwise in English
        8. exclude the introduction and unimportant data like the author story etc ,and always move to the first idea of pdf 
        Start your response with {{"""
        
        # Call DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational assessment creator. Generate high-quality, diverse multiple-choice questions. Always respond with valid JSON only, starting with '{'."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=10000,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        response_content = response.choices[0].message.content
        
        # Clean the response
        response_content = response_content.strip()
        
        # Remove any markdown code blocks
        if '```json' in response_content:
            response_content = response_content.split('```json')[1]
        elif '```' in response_content:
            response_content = response_content.split('```')[1]
        
        response_content = response_content.strip()
        
        # Ensure response starts with '{'
        if not response_content.startswith('{'):
            # Find the first '{' in the response
            start_index = response_content.find('{')
            if start_index != -1:
                response_content = response_content[start_index:]
            else:
                raise Exception("No JSON object found in response")
        
        # Parse JSON
        result = json.loads(response_content)
        questions = result.get('questions', [])
        
        # Validate and format questions
        validated_questions = []
        for i, q in enumerate(questions):
            # Ensure all required fields exist
            if not q.get('q') or not q.get('options'):
                continue
            
            # Validate options structure
            options = q['options']
            if not isinstance(options, dict) or len(options) < 4:
                continue
            
            validated_questions.append({
                'q': q['q'],
                'options': options,
                'ans': q.get('ans', 'A').upper(),
                'exp': q.get('exp', 'No explanation provided'),
            })
        
        # Limit to requested number
        final_questions = validated_questions[:num_questions]
        
        if not final_questions:
            raise Exception("No valid questions were generated from the text")
        
        return final_questions
        
    except json.JSONDecodeError as e:
        raise Exception(f"AI returned invalid JSON format: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate questions: {str(e)}")
