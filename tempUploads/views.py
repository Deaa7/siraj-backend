from datetime import datetime
 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TempUploadSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from services.backblaze_bucket_manager import delete_temp_uploads_from_bucket
 
 
 
from django.conf import settings
import boto3
from django.utils import timezone
from .models import TempUpload


# Create your views here.

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def upload_temp_file(request):
    serializer = TempUploadSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_temp_files(request):

         if delete_temp_uploads_from_bucket():
            return Response(status=status.HTTP_200_OK)
         return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_single_temp_file(request):

     name = request.data.get('name')
     print(name)
     temp_file = TempUpload.objects.filter(name=name).first()
     if not temp_file:
        return Response(status=status.HTTP_404_NOT_FOUND)

     client = boto3.client(
        's3',
        endpoint_url=settings.AWS_PRIVATE_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

     try:
 
            client.delete_objects(
                Bucket=settings.AWS_PRIVATE_BUCKET_NAME,
                Delete={
                    'Objects': [{'Key': name}],
                    'Quiet': True
                }
            )
            temp_file.delete()
            return Response(status=status.HTTP_200_OK)
     except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
