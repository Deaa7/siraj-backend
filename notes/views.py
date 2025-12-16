

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
 
from notesAppendixes.models import NotesAppendixes
from notesAppendixes.serializers import NotesAppendixesSerializer
from services.backblaze_bucket_manager import delete_file_from_b2
from utils.validators import CommonValidators

from services.parameters_validator import validate_pagination_parameters

from Constants import CLASSES_ARRAY , SUBJECT_NAMES_ARRAY , LEVELS_ARRAY 


# serializers
from .serializers import (
    NoteCardsSerializer,
    NoteCreateSerializer,
    NoteDataForEditSerializer,
    NoteDetailsForDashboardSerializer,
    NoteDetailsSerializer,
    NoteListDashboardSerializer,
    NotePreviewListSerializer,
    NoteUpdateSerializer,
    NoteContentSerializer,
)

# models 
from .models import Note
from teacherProfile.models import TeacherProfile
from studentPremiumContent.models import StudentPremiumContent
from teamProfile.models import TeamProfile
from users.models import User
from noteReadTracking.models import NoteReadTracking

# tasks 
from notifications.tasks import publishing_note_notification
from notesAppendixes.tasks import  process_existing_pdf_task

#services :
from services.publisher_plan_check import check_publisher_plan, check_publishing_content_availability


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def increase_number_of_downloads(request, note_public_id):
    try:
        note = get_object_or_404(Note, public_id=note_public_id)
        note.number_of_downloads += 1
        note.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def increase_number_of_purchases(request, note_public_id):
    try:
        note = Note.objects.get(public_id=note_public_id)
        note.number_of_purchases += 1
        note.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def change_number_of_comments(request, note_public_id):
    try:
        number = request.data.get("number", 1)
        note = Note.objects.get(public_id=note_public_id)
        note.number_of_comments += number
        note.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_note(request):
    try:
        user = get_object_or_404(User, id=request.user.id)
        publisher_id = user.id
        publisher_type = user.account_type
      
        if not check_publishing_content_availability(publisher_id, publisher_type, "note"):
            return Response(
                 "لقد تجاوزت الحد المسموح به لنشر النوطات", 
                status=status.HTTP_400_BAD_REQUEST
            )
        requestData = request.data;
        requestData["publisher_id"] =publisher_id
        serializer = NoteCreateSerializer(data=requestData)
        if serializer.is_valid():
            note = serializer.save()

            process_existing_pdf_task.delay(note.content, note.id)
            publishing_note_notification.delay(note.id, user.id , user.full_name)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response( str(e), status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["PATCH", "PUT"])
def update_note(request, note_public_id):
    try:
        publisher_id = request.user
        note = get_object_or_404(Note, public_id=note_public_id)

        if note.publisher_id != publisher_id:
            return Response(
                {"error": "غير مصرح لك بتحديث هذه النوطة"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Store the old content value to check if it changed
        old_content = note.content
        
        # Pass the instance to the serializer for update
        serializer = NoteUpdateSerializer(note, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        # Check if content field was updated and changed
        if "content" in request.data:
            # Refresh note from DB to get the updated content value
            note.refresh_from_db()
            new_content = note.content
            if new_content != old_content:
                # Content changed, update noteAppendixes using background task
                process_existing_pdf_task.delay(note.content, note.id)

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_note_data_for_edit(request , public_id):
        note = get_object_or_404(Note, public_id=public_id)
        serializer = NoteDataForEditSerializer(note)
    

        return Response(serializer.data, status=status.HTTP_200_OK)
    
        
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_note_details(request, note_public_id):
    try:
        source = request.data.get("source")  # purchase | course | public
        note = get_object_or_404(Note, public_id=note_public_id)
        
        check_publisher_plan(note.publisher_id)
        
        # here after we check the plan, we get the note again to make sure it is still active
        note = Note.objects.select_related("publisher_id").get(public_id=note_public_id)
        user = get_object_or_404(User, id=request.user.id)
        
        serializer = NoteDetailsSerializer(note)
        
        if not serializer.data["active"]:
            if source == "public":
                return Response(
                    {"error": "عذراً هذه النوطة لم تعد متوفرة"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        if source == "public" and note.visibility != "public":
            return Response(
                {"error": "عذراً هذه النوطة غير متوفرة للعرض بشكل عام"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        has_entered_before = NoteReadTracking.objects.filter(
            note_id=note,
            student_id=user,
        ).exists()

        is_purchased_before = True
        if note.price and note.price > 0:
            
            
            student_premium_content = StudentPremiumContent.objects.filter(
                note_id=note,
                student_id=user,
              
            )
            
            if student_premium_content.expiration_date > timezone.now():
                is_purchased_before = False
                student_premium_content.delete()
            else:
                is_purchased_before = True
        
        return Response(
            {
                "note_details": serializer.data,
                "is_purchased_before": is_purchased_before,
                "has_entered_before": has_entered_before,
            },
            status=status.HTTP_200_OK,
        )
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_note_cards(request):
    try:
        publisher_name = request.data.get("publisher_name")
        note_name = request.data.get("note_name")
        Class = request.data.get("Class")
        subject_name = request.data.get("subject_name")
        level = request.data.get("level")
        price = request.data.get("price")
        order_by = request.data.get("order_by")
        
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
        if order_by not in ["created_at" , "level" , "price" , "number_of_downloads"  , "number_of_pages"]:
         return Response(
                {"error": "الترتيب غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
         
        publisher_name = CommonValidators.validate_text_field(publisher_name)
        note_name = CommonValidators.validate_text_field(note_name)
        price = CommonValidators.validate_money_amount(price)
       
        
        # validate pagination parameters
        limit, count = validate_pagination_parameters(request.data.get("count", 0), request.data.get("limit", 7))
        
        notes = Note.objects.select_related("publisher_id").filter(active=True, visibility="public")

        if publisher_name:
            notes = notes.filter(publisher__full_name__icontains=publisher_name)
        if note_name:
            notes = notes.filter(name__icontains=note_name)
        if Class:
            notes = notes.filter(Class=Class)
        if subject_name:
            notes = notes.filter(subject_name=subject_name)
        if level:
            notes = notes.filter(level=level)
        if price:
            notes = notes.filter(price__lte=price)
        if order_by:
            notes = notes.order_by(order_by)

        begin = count * limit
        if begin > notes.count():
            begin = notes.count()
        end = (count + 1) * limit
        if end > notes.count():
            end = notes.count()

        serializer = NoteCardsSerializer(notes[begin:end], many=True)

        return Response(
            {"note_cards": serializer.data, "total_number": notes.count()},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_note_cards_by_publisher_public_id(request, publisher_public_id):
    try:
        count,limit = validate_pagination_parameters(request.query_params.get("count", 0), request.query_params.get("limit", 7))

        notes = Note.objects.select_related("publisher_id").filter(
            active=True, visibility="public", publisher_id__uuid=publisher_public_id
        ).order_by('-created_at')

        begin = count * limit
        if begin > notes.count():
            begin = notes.count()
        end = (count + 1) * limit
        if end > notes.count():
            end = notes.count()

        serializer = NoteCardsSerializer(notes[begin:end], many=True)

        return Response(
            {"note_cards": serializer.data, "total_number": notes.count()},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_notes_list_for_dashboard(request):
    try:
        publisher_id = request.user.id
        Class = request.query_params.get("Class")
        subject_name = request.query_params.get("subject_name")
        level = request.query_params.get("level")
        price = request.query_params.get("price")
        order_by = request.query_params.get("order_by")  # created_at , level ,price , number_of_downloads  , number_of_purchases , profit_amount
        active = request.query_params.get("active")
        name = request.query_params.get("name")
        
        if active == "true":
            active = True
        elif active == "false":
            active = False
    
        if name and len(name) > 0:
            name = CommonValidators.validate_text_field(name, "name")
        
        if active != "all" and active not in [True, False]:
            return Response(
                {"error": "الحالة غير متوفرة"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if Class != "all" and Class not in CLASSES_ARRAY:
            return Response(
                {"error": "الصف غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if subject_name != "all" and subject_name not in SUBJECT_NAMES_ARRAY:
            return Response(
                {"error": "المادة غير متوفرة"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if level != "all" and level not in LEVELS_ARRAY:
            return Response(
                {"error": "المستوى غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if order_by not in ["created_at" , "level" , "price" , "number_of_downloads"  , "number_of_purchases" , "profit_amount"]:
            return Response(
                {"error": "الترتيب غير متوفر"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if price != "all" and price != None:
         price = CommonValidators.validate_integer_field(price)
        
        count,limit= validate_pagination_parameters(request.query_params.get("count", 0), request.query_params.get("limit", 7))

        notes = Note.objects.filter(publisher_id=publisher_id).order_by('-created_at')

        if notes.count() <= 0:
            return Response(
                {"notes_list": [], "total_number": 0}, status=status.HTTP_204_NO_CONTENT
            )

        if name and len(name) > 0:
            notes = notes.filter(name__icontains=name)
        if Class != "all" and Class:
            notes = notes.filter(Class=Class)
        if subject_name != "all" and subject_name:
            notes = notes.filter(subject_name=subject_name)
        if level != "all" and level:
            notes = notes.filter(level=level)
        if price != "all" and price:
            notes = notes.filter(price__lte=price)
        if active != "all" and active is not None:
            notes = notes.filter(active=active)

        if order_by != "created_at":
            notes = notes.order_by(order_by)

        begin = count * limit
        if begin > notes.count():
            begin = notes.count()
            
        end = (count + 1) * limit
        if end > notes.count():
            end = notes.count()
        
        serializer = NoteListDashboardSerializer(notes[begin:end], many=True)


        return Response(
            {"notes_list": serializer.data, "total_number": notes.count()},
            status=status.HTTP_200_OK,
        )
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_note(request, note_public_id):
    
    note = get_object_or_404(Note, public_id=note_public_id)
    
    try:
        publisher_id = request.user.id
        publisher = get_object_or_404(User, id=publisher_id)
        publisher_type = publisher.account_type  # teacher, team
        
        publisher_record = None

        if publisher_type == "teacher":
            publisher_record = get_object_or_404(TeacherProfile, user=publisher)
        elif publisher_type == "team":
            publisher_record = get_object_or_404(TeamProfile, user=publisher)

        # check if a student has purchased the note, in this case we can't delete the note
        student_premium_content = StudentPremiumContent.objects.filter(
            note_id=note.id, date_of_expiration__gte=timezone.now()
        )

        if student_premium_content.exists():
            return Response(
                {"error": " عذراً لا يمكنك حذف هذه النوطة لأنه تم شراؤها من قبل طلاب"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        
        delete_file_from_b2(note.content)
      
        note.delete()
        publisher_record.number_of_notes -= 1
        publisher_record.save()        

        return Response({"message": "تم حذف النوطة بنجاح"}, status=status.HTTP_200_OK)
   
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_note_details_for_dashboard(request, note_public_id):
    try:
        publisher_id = request.user
        note = Note.objects.select_related("publisher_id").get(public_id=note_public_id)

        if publisher_id != note.publisher_id:
            return Response(
                {"error": "غير مصرح لك بعرض تفاصيل هذه النوطة"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = NoteDetailsForDashboardSerializer(note)
        return Response({"note_details": serializer.data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_note_content(request, note_public_id):
    try:
        note = get_object_or_404(Note, public_id=note_public_id)
        serializer = NoteContentSerializer(note)
        
        note_appendix = NotesAppendixes.objects.get_or_create(note_id=note.id)
        note_appendix_serializer = NotesAppendixesSerializer(note_appendix)
        
        return Response({"note_content": serializer.data, "note_appendix": note_appendix_serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_note_preview_list(request):
    try:
        user = request.user
        notes = Note.objects.select_related("publisher_id").filter(publisher_id=user.id , price__gt = 0 )
        serializer = NotePreviewListSerializer(notes, many=True)
        return Response({"notes": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
