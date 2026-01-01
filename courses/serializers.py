import json
from rest_framework import serializers
from .models import Course
from utils.validators import CommonValidators

from Constants import SUBJECT_NAMES_ARRAY, CLASSES_ARRAY, LEVELS_ARRAY

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "name",
            "subject_name",
            "Class",
            "publisher_id",
            "what_you_will_learn",
            "description",
            "price",
            "number_of_lessons",
            "course_image",
            "estimated_time",
            "level",
        ]
        
        
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("اسم الدورة مطلوب")
        return CommonValidators.validate_text_field(value, "اسم الدورة", max_length=300)
    
    def validate_subject_name(self, value):
 
        if not value:
            raise serializers.ValidationError("اسم المادة مطلوب")
 
        if not value in SUBJECT_NAMES_ARRAY:
            raise serializers.ValidationError("اسم المادة غير موجود")
 
        return value
    
    def validate_Class(self, value):
 
        if not value:
            raise serializers.ValidationError("الصف مطلوب")
 
        if not value in CLASSES_ARRAY:
            raise serializers.ValidationError("الصف غير موجود")
 
        return value
 
    def validate_what_you_will_learn(self, value):
        """Validate comment text with security protection for Arabic, English, and numbers"""
        if not value:
            raise serializers.ValidationError(
                "ما الذي سيتعلمه الطلاب من هذا الدرس مطلوب"
            )
        val = json.loads(value)
        if not val:
            raise serializers.ValidationError("ما الذي سيتعلمه الطلاب من هذا الدرس مطلوب")
        for item in val:
            if not item:
                raise serializers.ValidationError("ما الذي سيتعلمه الطلاب من هذا الدرس مطلوب")
            CommonValidators.validate_text_field(
            item, "ما الذي سيتعلمه الطلاب من هذا الدرس", max_length=2000
        )
        return value

    def validate_price(self, value):
    
        return CommonValidators.validate_money_amount(value, "السعر")
    
     
class CourseDetailSerializer(serializers.ModelSerializer):
    
    publisher_name = serializers.SerializerMethodField("get_publisher_name")
    publisher_public_id = serializers.CharField(source="publisher_id.uuid")
    class Meta:
        model = Course
        fields = [
            "public_id",
            "name",
            "subject_name",
            "Class",
            "publisher_name",
            "publisher_public_id",
            "what_you_will_learn",
            "description",
            "price",
            "number_of_lessons",
            "number_of_enrollments",
            "number_of_comments",
            "number_of_purchases",
            "number_of_completions",
            "created_at",
            "updated_at",
            "active",
            "course_image",
            "level",
            "estimated_time",
        ]

    def get_publisher_name(self, obj):
        name = ""
        if obj.publisher_id.account_type == "teacher":
            name = "الاستاذ " if obj.publisher_id.gender == "M" else "الآنسة " 
            name += obj.publisher_id.full_name
        elif obj.publisher_id.account_type == "team":
            name = "فريق " + obj.publisher_id.team_name
        return name
    
    
class CourseListParametersSerializer(serializers.Serializer):

    course_name = serializers.CharField(required=False)
    Class = serializers.CharField(required=False)
    subject_name = serializers.CharField(required=False)
    level = serializers.CharField(required=False)
    price = serializers.CharField(required=False)
    order_by = serializers.CharField(required=False)
    publisher_name = serializers.CharField(required=False)
    
    def validate_course_name(self, value):

        return CommonValidators.validate_text_field(value, "اسم الدرس", max_length=300)

    def validate_Class(self, value):
        if not value:
            return None
        if not value in CLASSES_ARRAY:
            raise serializers.ValidationError("الصف غير موجود")
        return value

    def validate_subject_name(self, value):
        if not value:
           return None
        if not value in SUBJECT_NAMES_ARRAY:
            raise serializers.ValidationError("اسم المادة غير موجود")
        return value
    
    def validate_level(self, value):
        if not value:
            return None
        if not value in LEVELS_ARRAY:
            raise serializers.ValidationError("المستوى غير موجود")
        return value

    def validate_price(self, value):
        if not value:
            return 0
        return CommonValidators.validate_money_amount(value, "السعر")
 
    def validate_publisher_name(self, value):
        if not value:
            return None
        return CommonValidators.validate_text_field(value, "اسم الناشر", max_length=300)

class CourseListSerializer(serializers.ModelSerializer):
    
    publisher_name = serializers.SerializerMethodField("get_publisher_name")
    
    publisher_public_id = serializers.CharField(source="publisher_id.uuid")
    class Meta:
        model = Course
        fields = [
            "public_id",
            "name",
            "subject_name",
            "Class",
            "publisher_name",
            "publisher_public_id",
            "price",
            "course_image",
            "description",
            "estimated_time",
            "number_of_lessons",
            "number_of_enrollments",
            "number_of_completions",
            "number_of_comments",
            "active",
            "level",
        ]
        
    def get_publisher_name(self, obj):
        name = ""
        if obj.publisher_id.account_type == "teacher":
            name = "الاستاذ " if obj.publisher_id.gender == "M" else "الآنسة " 
            name += obj.publisher_id.full_name
        elif obj.publisher_id.account_type == "team":
            name = "فريق " + obj.publisher_id.team_name
        return name
    

class CourseUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = [
            "name",
            "subject_name",
            "Class",
            "description",
            "price",
            "level",
            "what_you_will_learn",
            "course_image",
            "estimated_time",
        ]

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("اسم الدرس مطلوب")
        return CommonValidators.validate_text_field(value, "اسم الدرس", max_length=300)

    def validate_description(self, value):
 
        return CommonValidators.validate_text_field(value, "الوصف", max_length=1000 , allow_empty=True)

    def validate_price(self, value):
        return CommonValidators.validate_money_amount(value, "السعر")

    def validate_what_you_will_learn(self, value):
        if not value:
            raise serializers.ValidationError(
                "ما الذي سيتعلمه الطلاب من هذا الدرس مطلوب"
            )
        val = json.loads(value)
        if not val:
            raise serializers.ValidationError("ما الذي سيتعلمه الطلاب من هذا الدرس مطلوب")
        for item in val:
            if not item:
                raise serializers.ValidationError("ما الذي سيتعلمه الطلاب من هذا الدرس مطلوب")
            CommonValidators.validate_text_field(
            item, "ما الذي سيتعلمه الطلاب من هذا الدرس", max_length=2000
        )
        return CommonValidators.validate_text_field(
            value, "ما الذي سيتعلمه الطلاب من هذا الدرس", max_length=2000
        )

    def validate_estimated_time(self, value):
        if not value:
            raise serializers.ValidationError("الوقت المقدر مطلوب")
        return CommonValidators.validate_money_amount(value, "الوقت المقدر")
    
    
class CourseListDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "public_id",
            "name",
            "Class",
            "subject_name",
            "price",
            "number_of_enrollments",
            "number_of_completions",
            "number_of_purchases",
            "profit_amount",
            "level",
            "active",
            "estimated_time"
        ]
      
  
class CourseDetailsForDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "public_id",
            "name",
            "Class",
            "subject_name",
            "price",
            "number_of_enrollments",
            "number_of_completions",
            "number_of_purchases",
            "number_of_lessons",
            "number_of_comments",
            "profit_amount",
            "level",
            "active",
            "what_you_will_learn",
            "description",
            "estimated_time",
            "created_at",
            "updated_at",
            "course_image",
        ]
        
        
        
class CoursePreviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "public_id",
            "name",
            "price",
        ]