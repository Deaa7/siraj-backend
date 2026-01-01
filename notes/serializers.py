from rest_framework import serializers
from .models import Note
from utils.security import SecurityValidator
from django.core.exceptions import ValidationError
from django.conf import settings
import boto3
from botocore.config import Config
from utils.validators import CommonValidators

class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "name",
            "price",
            "subject_name",
            "Class",
            "level",
            "visibility",
            "publisher_id",
            "description",
            "content",
            "number_of_pages",
            "file_size",
            "file_unique_name",
        ]
        
class NoteDetailsSerializer(serializers.ModelSerializer):
    publisher_public_id = serializers.CharField(source="publisher_id.uuid")
    publisher_name = serializers.SerializerMethodField("get_publisher_name")
    class Meta:
        model = Note
        fields = [
            "name",
            "subject_name",
            "Class",
            "level",
            "visibility",
            "publisher_public_id",
            "publisher_name",
            "description",
            "number_of_pages",
            "file_size",
            "number_of_downloads",
            "number_of_comments",
            "price",
            "created_at",
            "updated_at",
        ]
        
    def get_publisher_name(self, obj):
        name = ""
        if obj.publisher_id.account_category == "teacher":
            name = "الاستاذ " if obj.publisher_id.gender == "M" else "الآنسة " 
            name += obj.publisher_id.full_name
        elif obj.publisher_id.account_category == "team":
            name = "فريق " + obj.publisher_id.team_name
        return name
      
    
class NoteDataForEditSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField("get_presigned_url")
    class Meta:
        model = Note
        fields = [
            "name",
            "subject_name",
            "Class",
            "level",
            "visibility",
             "description",
            "url" ,
            "price",
            "content",
        ]
        
    def get_presigned_url(self, obj):
        
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
                 'Key': obj.content,
                'ResponseContentType': 'application/pdf',
            },
            ExpiresIn=3600
        )
          
          return presigned_url
      
    

class NoteListDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "public_id",
            "name",
            "subject_name",
            "Class",
            "level",
             "price",
             "number_of_downloads",
             "number_of_purchases",
             "profit_amount",
             "active",
        ]
        
        
class NoteDetailsForDashboardSerializer(serializers.ModelSerializer):
    publisher_public_id = serializers.CharField(source="publisher_id.uuid")
    class Meta:
        model = Note
        fields = [
            "public_id",
            "active",   
            "name",
            "subject_name",
            "Class",
            "level",
            "price",
            "profit_amount",
            "description",
            "publisher_public_id",
            "number_of_downloads",
            "number_of_purchases",
            "number_of_comments",
            "number_of_pages",
            "file_size",
            "created_at",
            "updated_at",
            "visibility",
        ]
 
      
class NoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "name",
            "subject_name",
            "Class",
            "level",
            "visibility",
            "price",
            "description",
            "content"
        ]
        
       
    def validate_name(self, value):
        """Validate name with global security protection"""
        if not value:
            return value

        try:
            return SecurityValidator.validate_input(
                value, "اسم النوطة",
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_description(self, value):
        """Validate description with global security protection"""
        if not value:
            return value

        try:
            return SecurityValidator.validate_input(
                value, "وصف النوطة",
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_price(self, value):
        """Validate price with global security protection"""
        return CommonValidators.validate_money_amount(value)

    def validate_visibility(self, value):
        """Validate visibility with global security protection"""
        if not value:
            return value
        if value not in ["public", "course"]:
            raise serializers.ValidationError("البيانات غير صالحة")
        return value

    def validate(self, data):
        """Cross-field validation"""
        # Check if at least one field is provided
        if not any(data.values()):
            raise serializers.ValidationError("يجب توفير حقل واحد على الأقل للتحديث")

        return data
    
class NoteCardsSerializer(serializers.ModelSerializer):
    publisher_public_id = serializers.CharField(source="publisher_id.uuid")
    publisher_name = serializers.SerializerMethodField("get_publisher_name")
    class Meta:
        model = Note
        fields = [
            "public_id",
            "name",
            "subject_name",
            "Class",
            "level",
            "price",
            "description",
            "number_of_downloads",
            "number_of_comments",
            "file_size",
            "number_of_pages",
            "publisher_public_id",
            "publisher_name",
        ]
        
    def get_publisher_name(self, obj):
        name = ""
        if obj.publisher_id.account_type == "teacher":
            name = "الاستاذ " if obj.publisher_id.gender == "M" else "الآنسة " 
            name += obj.publisher_id.full_name
        elif obj.publisher_id.account_type == "team":
            name = "فريق " + obj.publisher_id.team_name
        return name
      
      
      
class NoteContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "public_id"
            "number_of_pages",
            "file_size",
            "file_unique_name",
            "content",
        ]
        
class NotePreviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "public_id",
            "name",
            "price",
        ]