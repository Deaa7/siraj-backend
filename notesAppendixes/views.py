from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import NotesAppendixes
from .serializers import NotesAppendixesSerializer


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_note_appendix(request):
    serializer = NotesAppendixesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_note_appendix(request, note_public_id):
    appendix = get_object_or_404(
        NotesAppendixes, note_id__public_id=note_public_id
    )
    serializer = NotesAppendixesSerializer(appendix)
    return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["PATCH"])
def update_note_appendix(request, note_public_id):
    appendix = get_object_or_404(
        NotesAppendixes, note_id__public_id=note_public_id
    )
    serializer = NotesAppendixesSerializer(
        appendix, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_note_appendix(request, note_public_id):
    appendix = get_object_or_404(
        NotesAppendixes, note_id__public_id=note_public_id
    )
    appendix.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
