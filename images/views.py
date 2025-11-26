from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from posts.models import Post
from .models import Image
from .serializers import ImageSerializer

from services.backblaze_bucket_manager import delete_file_from_b2


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_images_by_post(request, post_public_id):
    post = get_object_or_404(Post, public_id=post_public_id)
    images = Image.objects.filter(post=post)
    serializer = ImageSerializer(images, many=True)
    return Response({'images': serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_image(request, post_public_id):
    post = get_object_or_404(Post, public_id=post_public_id)

    serializer = ImageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    Image.objects.create(
        post=post,
        image=serializer.validated_data['image'],
    )

    return Response(status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_image(request, image_public_id):
   
   image = get_object_or_404(Image, public_id=image_public_id)
   delete_file_from_b2(image.image)
   image.delete()
   
   return Response(status=status.HTTP_204_NO_CONTENT)
        
