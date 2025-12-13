from rest_framework import serializers
from .models import Note
from utils.security import SecurityValidator
from django.core.exceptions import ValidationError
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
            # "number_of_reads",
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
                value, "اسم النوطة", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_description(self, value):
        """Validate description with global security protection"""
        if not value:
            return value

        try:
            return SecurityValidator.validate_input(
                value, "وصف النوطة", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_price(self, value):
        """Validate price with global security protection"""
        if not value:
            return value
        try:
            if not isinstance(value, (int, float)):
                raise serializers.ValidationError("السعر يجب ان يكون رقم صحيح")
            if value < 0:
                raise serializers.ValidationError("السعر يجب ان يكون اكبر من 0")
            if value > 1000000:
                raise serializers.ValidationError("السعر يجب ان يكون اقل من 1000000")
            return value
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

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