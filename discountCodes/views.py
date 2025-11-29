from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from services.parameters_validator import validate_pagination_parameters
from utils.validators import CommonValidators

# models
from .models import DiscountCodes
from users.models import User
from exams.models import Exam
from notes.models import Note
from courses.models import Course

# serializers
from .serializers import (
    DiscountCodeCreateSerializer,
    DiscountCodeListSerializer,
    DiscountCodeUpdateSerializer,
    DiscountCodeValidateSerializer,
)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_discount_code(request):
    try:
        user = get_object_or_404(User, id=request.user.id)
        publisher_id = user.id
         
        if user.account_type  == "student" : 
            return  Response( {"غير مصرح لك بإنشاء كود خصم"} , status.HTTP_403_FORBIDDEN )
        # Get content_public_id and discount_for from request
        content_public_id = request.data.get("content_public_id")
        discount_for = request.data.get("discount_for")
        discount_code = request.data.get("discount_code")
        
        discount_code = CommonValidators.validate_text_field(discount_code, "discount_code")
        
        if discount_for not in ["exam", "note", "course" , "offer"]:
            return Response(
                {"error": "نوع الخصم غير صحيح. "},
                status=status.HTTP_400_BAD_REQUEST
            )
       
        if not content_public_id:
            return Response(
                {"error": "معرف المحتوى مطلوب"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find the actual content record based on discount_for and content_public_id
        content_record = None
        if discount_for == "exam":
            content_record = get_object_or_404(Exam, public_id=content_public_id)
            # Verify that the publisher owns this exam
            if content_record.publisher_id.id != publisher_id:
                return Response(
                    {"error": "غير مصرح لك بإنشاء كود خصم لهذا الامتحان"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        elif discount_for == "note":
            content_record = get_object_or_404(Note, public_id=content_public_id)
            # Verify that the publisher owns this note
            if content_record.publisher_id.id != publisher_id:
                return Response(
                    {"error": "غير مصرح لك بإنشاء كود خصم لهذه النوطة"},
                    status=status.HTTP_403_FORBIDDEN
                )
       
        elif discount_for == "course":
            content_record = get_object_or_404(Course, public_id=content_public_id)
            # Verify that the publisher owns this course
            if content_record.publisher_id.id != publisher_id:
                return Response(
                    {"error": "غير مصرح لك بإنشاء كود خصم لهذه الدورة"},
                    status=status.HTTP_403_FORBIDDEN
                )
 
            return Response(
                {"error": "نوع الخصم غير صحيح. "},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare data for serializer
        data = request.data.copy()  
        data["publisher_id"] = publisher_id
        
        # Assign the appropriate foreign key based on discount_for
        if discount_for == "exam":
            data["exam_id"] = content_record.id
            data["note_id"] = None
            data["course_id"] = None
            data["offer_id"] = None
        elif discount_for == "note":
            data["exam_id"] = None
            data["note_id"] = content_record.id
            data["course_id"] = None
            data["offer_id"] = None
        elif discount_for == "course":
            data["exam_id"] = None
            data["note_id"] = None
            data["course_id"] = content_record.id
            data["offer_id"] = None
        
        data["discount_code"] = discount_code 
        
        serializer = DiscountCodeCreateSerializer(data=data)
        
        if serializer.is_valid():
            discount_code = serializer.save()
            return Response(
                {"message": "تم إنشاء كود الخصم بنجاح"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH", "PUT"])
def update_discount_code(request, discount_code_public_id):
    try:
        publisher_id = request.user.id
        discount_code = get_object_or_404(DiscountCodes, public_id=discount_code_public_id)

        if discount_code.publisher_id.id != publisher_id:
            return Response(
                {"error": "غير مصرح لك بتعديل كود الخصم هذا"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Pass the instance to the serializer for update
        serializer = DiscountCodeUpdateSerializer(discount_code, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()

        return Response(
            {"message": "تم تحديث كود الخصم بنجاح"},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

 
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_discount_codes_list(request):
    try:
        publisher_id = request.user.id
        
        count, limit = validate_pagination_parameters(request.query_params.get("count", 0), request.query_params.get("limit", 10))
        
        discount_codes = DiscountCodes.objects.select_related("exam_id", "note_id", "course_id").filter(publisher_id=publisher_id).order_by("-created_at")
        
 
        total = discount_codes.count()
        begin = count * limit
        if begin > total:
            begin = total
        end = (count + 1) * limit
        if end > total:
            end = total
        
        serializer = DiscountCodeListSerializer(discount_codes[begin:end], many=True)
        
        return Response(
            {
                "discount_codes": serializer.data,
                "total_number": total
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_discount_code(request, discount_code_public_id):
    try:
        publisher_id = request.user.id
        discount_code = get_object_or_404(DiscountCodes, public_id=discount_code_public_id)

        if discount_code.publisher_id.id != publisher_id:
            return Response(
                {"error": "غير مصرح لك بحذف كود الخصم هذا"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        discount_code.delete()
        return Response(
            {"message": "تم حذف كود الخصم بنجاح"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def validate_discount_code(request):
    """
    Validate a discount code by code string
    """
    try:
    
        serializer = DiscountCodeValidateSerializer(data=request.data)
       
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
        return Response(
            {
                "message": "كود الخصم صالح",
                "discount_data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_discount_codes_list_by_content_public_id(request, content_public_id):
    try:
        
        limit, count = validate_pagination_parameters(request.data.get("count", 0), request.data.get("limit", 10))
        begin = count * limit

        discount_codes = DiscountCodes.objects.select_related("exam_id", "note_id", "course_id").filter(exam_id__public_id=content_public_id, note_id__public_id=content_public_id, course_id__public_id=content_public_id)
        
        if begin > discount_codes.count():
            begin = discount_codes.count()
        
        end = (count + 1) * limit
        
        if end > discount_codes.count():
            end = discount_codes.count()
            
            
        serializer = DiscountCodeListSerializer(discount_codes[begin:end], many=True)
        
        
        return Response(
            {
                "discount_codes": serializer.data,
                "total_number": discount_codes.count()
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

