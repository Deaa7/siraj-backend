from rest_framework import serializers
from .models import Exam
from utils.security import SecurityValidator
from django.core.exceptions import ValidationError
from utils.validators import CommonValidators

class ExamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            "name",
            "publisher_id",
            "subject_name",
            "Class",
            "units",
            "level",
            "number_of_questions",
            "description",
            "price",
            "visibility",
        ]

    def validate_name(self, value):
        """Validate name with global security protection"""
        if not value:
            raise serializers.ValidationError("اسم الامتحان مطلوب")

        try:
            return SecurityValidator.validate_input(
                value, "اسم الامتحان", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_description(self, value):
        """Validate description with global security protection"""
        if not value:
            return value

        try:
            return SecurityValidator.validate_input(
                value, "المواد الدراسية", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_price(self, value):
        """Validate price with global security protection"""
        # Allow None or empty string (if price is optional)
        if value is None or (isinstance(value, str) and not value.strip()):
            return value
        try:
            return CommonValidators.validate_money_amount(value, "السعر")
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_visibility(self, value):
        """Validate visibility with global security protection"""
        if not value:
            return value
        if value not in ["public", "course"]:
            raise serializers.ValidationError("البيانات غير صالحة")
        return value


class ExamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            "name",
            "subject_name",
            "Class",
            "units",
            "level",
            "description",
            "price",
            "visibility",
        ]

    def validate_name(self, value):
        """Validate name with global security protection"""
        if not value:
            return value

        try:
            return SecurityValidator.validate_input(
                value, "اسم الامتحان", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_description(self, value):
        """Validate description with global security protection"""
        if not value:
            return value

        try:
            return SecurityValidator.validate_input(
                value, "المواد الدراسية", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_price(self, value):
        """Validate price with global security protection"""
        if not value:
            return value
        try:
            if not isinstance(value, (int, float)):
                raise serializers.ValidationError("السعر يجب ان يكون عدد صحيح")
            if value < 0:
                raise serializers.ValidationError("السعر يجب ان يكون اكبر من 0")
            if value > 10000000:
                raise serializers.ValidationError("السعر يجب ان يكون اقل من 10000000")
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


class ExamCardsSerializer(serializers.ModelSerializer):
    publisher_public_id = serializers.CharField(source="publisher_id.uuid")
    publisher_name = serializers.SerializerMethodField("get_publisher_name")
    
    class Meta:
        model = Exam
        fields = [
            "public_id",
            "name",
            "publisher_public_id",
            "publisher_name",
            "subject_name",
            "Class",
            "level",
            "number_of_questions",
            "number_of_apps",
            "description",
            "price",
            "result_avg",
        ]
    
    def get_publisher_name(self, obj):
        name = ""
        if obj.publisher_id.account_type == "teacher":
            name = "الاستاذ " if obj.publisher_id.gender == "M" else "الآنسة " 
            name += obj.publisher_id.full_name
        elif obj.publisher_id.account_type == "team":
            name = "فريق " + obj.publisher_id.team_name
        return name


class ExamDetailsSerializer(serializers.ModelSerializer):
    publisher_public_id = serializers.CharField(source="publisher_id.uuid")
    publisher_name = serializers.SerializerMethodField("get_publisher_name")
    
    class Meta:
        model = Exam
        fields = [
            "public_id",
            "name",
            "publisher_public_id",
            "publisher_name",
            "subject_name",
            "Class",
            "level",
            "number_of_questions",
            "number_of_apps",
            "number_of_comments",
            "description",
            "price",
            "result_avg",
            "active",
            "units",
            "created_at",
            "updated_at",
        ]
    
    def get_publisher_name(self, obj):
        name = ""
        if obj.publisher_id.account_type == "teacher":
            name = "الاستاذ " if obj.publisher_id.gender == "M" else "الآنسة " 
            name += obj.publisher_id.full_name
        elif obj.publisher_id.account_type == "team":
            name = "فريق " + obj.publisher_id.team_name
        return name


class ExamDetailsForDashboardSerializer(serializers.ModelSerializer):
    publisher_public_id = serializers.CharField(source="publisher_id.uuid")
    publisher_name = serializers.SerializerMethodField("get_publisher_name")
    
    class Meta:
        model = Exam
        fields = [
            "public_id",
            "name",
            "subject_name",
            "Class",
            "level",
            "number_of_questions",
            "number_of_apps",
            "number_of_comments",
            "number_of_purchases",
            "description",
            "price",
            "profit_amount",
            "result_avg",
            "active",
            "units",
            "publisher_public_id",
            "publisher_name",
            "visibility",
            "created_at",
            "updated_at",
        ]
    
    def get_publisher_name(self, obj):
        name = ""
        if obj.publisher_id.account_type == "teacher":
            name = "الاستاذ " if obj.publisher_id.gender == "M" else "الآنسة " 
            name += obj.publisher_id.full_name
        elif obj.publisher_id.account_type == "team":
            name = "فريق " + obj.publisher_id.team_name
        return name


class ExamListDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            "public_id",
            "name",
            "subject_name",
            "Class",
            "active",
            "level",
            "price",
            "number_of_apps",
            "number_of_purchases",
            "profit_amount",
            "result_avg",
        ]


class ExamPreviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = [
            "public_id",
            "name",
        ]
  