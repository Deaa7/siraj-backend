from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Videos
from tempUploads.models import TempUpload
from .serializers import VideoSerializer
from django.conf import settings
import boto3
from botocore.config import Config



@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_videos(request , public_id):

  video = Videos.objects.get(public_id=public_id)
  
  response = {
      "public_id" : video.public_id ,
      "video_url" : video.video_url ,
      "file_size" : video.file_size ,
      "file_unique_name" : video.file_unique_name , 
      "video_explanation" : video.video_explanation  ,
  }  
  
  return Response(response, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_video(request):
  
  validated_data = VideoSerializer(data=request.data)
  if not validated_data.is_valid():
    return Response(validated_data.errors, status=status.HTTP_400_BAD_REQUEST)
  validated_data.save()
  
  return Response(status=status.HTTP_201_CREATED)


@permission_classes([IsAuthenticated])
@api_view(['PUT' , 'PATCH'])
def update_video(request, public_id):
  
  video = Videos.objects.get(public_id=public_id)
  validated_data = VideoSerializer(data=request.data , partial=True)
  
  if not validated_data.is_valid():
    return Response(validated_data.errors, status=status.HTTP_400_BAD_REQUEST)
  
  video.video_explanation = validated_data.validated_data['video_explanation']
  
  if validated_data.validated_data['video_file']: # set to null if the user did not upload a new video
    video_file = validated_data.validated_data['video_file']
    file_size = video_file.size
    video_url = upload_file_to_bucket(video_file)
    video.video_url = video_url
    video.file_size = file_size
 
  video.save()  
  return Response(status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_video(request, public_id):

 try:  
  video = Videos.objects.get(public_id=public_id)
  video.delete()
  return Response(status=status.HTTP_200_OK)
 
 except Exception as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_video_presigned_url(request):

 try: 
  name = request.query_params.get('name')
  s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_PRIVATE_ENDPOINT_URL,  # Your Backblaze endpoint
             region_name=settings.AWS_PRIVATE_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,  # Your keyID
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,  # Your applicationKey
            config=Config(signature_version='s3v4'),
        )

  presigned_url = s3_client.generate_presigned_url(
                 ClientMethod="get_object",
            Params={
                'Bucket': settings.AWS_PRIVATE_BUCKET_NAME,
                 'Key': name,
                'ResponseContentType': 'application/pdf',
            },
            ExpiresIn=36000
        )
  return Response({ 'url' :presigned_url  } , status = status.HTTP_200_OK)
 except Exception as e:
   return Response({ 'message' :"حدث خطأ أثناء جلب الملف"  } , status = status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
@permission_classes([IsAuthenticated])
@api_view(['POST'])    
def delete_video_from_bucket(request):
          # Initialize B2/S3 client

        """
        Delete a file from Backblaze B2 bucket using file key/name
        """
        file_key = request.data.get('name');
        
        temp_upload = TempUpload.objects.get(name=file_key)
    
        client = boto3.client(
            's3',
            endpoint_url=settings.AWS_PRIVATE_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        
        try:
            # Delete the object from B2 bucket
            client.delete_object(
                Bucket=settings.AWS_PRIVATE_BUCKET_NAME,
                Key=file_key
            )
            if temp_upload is not None: 
             temp_upload.delete()
 
            return Response({
                'success': True,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
             
            return Response({
                'error': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)