from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework import status

from studentSubjectTracking.models import StudentSubjectTracking
from .serializers import NoteReadTrackingCardsSerializer
from .models import NoteReadTracking
from notes.models import Note
from django.shortcuts import get_object_or_404
from services.parameters_validator import validate_pagination_parameters

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_note_read_tracking(request, note_public_id):

    try:

        user = request.user  # student info
        note = get_object_or_404(Note, public_id=note_public_id)

        if user is None:
            return Response({"error": "مستخدم غير موجود"}, status=status.HTTP_404_NOT_FOUND)

        note_read_tracking, created = NoteReadTracking.objects.get_or_create(
            note_id=note,
            student_id=user,
            number_of_reads=1,
        )   

        if created:
            subject_tracking = StudentSubjectTracking.objects.get(
                student_id=user,
                subject_name=note.subject_name,
            )
            
            subject_tracking.number_of_notes += 1
            subject_tracking.save()
        
        note.number_of_downloads += 1
        note.save()

        return Response(status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_note_read_tracking_cards(request, public_student_id):

    try:

        limit, count = validate_pagination_parameters(request.data.get("count", 0), request.data.get("limit", 10))

        begin = count * limit
        end = (count + 1) * limit

        note_read_trackings = NoteReadTracking.objects.select_related('note_id', 'student_id').filter(
            student_id__uuid=public_student_id
        )

        serializer = NoteReadTrackingCardsSerializer(note_read_trackings[begin:end], many=True)

        return Response(
            {"note_tracking_cards": serializer.data, "count": len(note_read_trackings)},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def update_note_read_tracking_metrics(request, note_public_id):

    try:
        user = request.user  # student info
        note = get_object_or_404(Note, public_id=note_public_id)

        if user is None:
            return Response({"error": "مستخدم غير موجود"}, status=status.HTTP_404_NOT_FOUND)

        note_read_tracking = get_object_or_404(NoteReadTracking, note_id=note, student_id=user)
        # Update tracking metrics here
        note_read_tracking.number_of_reads += 1
 
        note_read_tracking.save()
        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
