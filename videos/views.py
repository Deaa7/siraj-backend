from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Videos
from .serializers import VideoSerializer
import uuid
from services.backblaze_bucket_manager import delete_file_from_b2, upload_file_to_bucket
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

  video_file = validated_data.validated_data['video_file']
  video_explanation = validated_data.validated_data['video_explanation']
  file_size = video_file.size
  video_unique_name = uuid.uuid4()
  video_url = upload_file_to_bucket(video_file)
  
  Videos.objects.create(video_url=video_url, file_size=file_size, file_unique_name=video_unique_name, video_explanation=video_explanation)

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
  delete_file_from_b2(video.video_url)
  video.delete()
  return Response(status=status.HTTP_200_OK)
 
 except Exception as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


