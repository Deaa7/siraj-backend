from rest_framework import serializers

from .models import Post
from images.models import Image
from utils.validators import CommonValidators


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["image"]


class PostCreateSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = Post
        fields = ["content", "allowed_comments" ]

    def validate_content(self, value):
        return CommonValidators.validate_text_field(
            value, field_name="محتوى المنشور", max_length=10000
        )


class PostUpdateSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Post
        fields = ["content", "allowed_comments", "active"]

    def validate_content(self, value):
        if value is None:
            return value
        return CommonValidators.validate_text_field(
            value, field_name="محتوى المنشور", max_length=10000
        )


# class PostDetailSerializer(serializers.ModelSerializer):



class PostListSerializer(serializers.ModelSerializer):
  
    publisher_public_id = serializers.CharField(source="user.uuid")
    publisher_name = serializers.SerializerMethodField(method_name="get_publisher_name")
    publisher_type = serializers.CharField(source="user.account_type")
    publisher_image = serializers.CharField(source="user.image", allow_blank=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "public_id",
            "content",
            "allowed_comments",
            "number_of_comments",
            "created_at",
            "updated_at",
            "publisher_public_id",
            "publisher_name",
            "publisher_type",
            "publisher_image",
            "images",
        ]

    def get_publisher_name(self, obj: Post):
        return obj.user.full_name

    def get_images(self, obj: Post):
        
        images = Image.objects.filter(post=obj)
        return [image.image for image in images]