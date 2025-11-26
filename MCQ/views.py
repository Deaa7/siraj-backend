from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404

# Create your views here.
from .models import MCQ
from .serializers import MCQSerializer
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def create_mcq(request):
    serializer = MCQSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_exam_mcqs(request):
    exam_id = request.data.get("exam_id")
    mcqs = MCQ.objects.filter(exam_id=exam_id)
    serializer = MCQSerializer(mcqs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["PUT" , "PATCH"])
def edit_mcq(request , mcq_public_id):
    mcq = get_object_or_404(MCQ, public_id=mcq_public_id)
    serializer = MCQSerializer(mcq, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_mcq(request , mcq_public_id):
    mcq = get_object_or_404(MCQ, public_id=mcq_public_id)
    mcq.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

 