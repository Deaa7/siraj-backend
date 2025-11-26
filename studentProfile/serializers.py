from rest_framework import serializers
from .models import StudentProfile
from rest_framework import serializers
from utils.security import SecurityValidator
from django.core.exceptions import ValidationError
from users.serializers import UserUpdateSerializer


class StudentProfileResponseSerializer(serializers.ModelSerializer):
    """Serializer for student profile response"""

    class Meta:
        model = StudentProfile
        fields = [
            "first_name",
            "last_name",
            "city",
            "gender",
            "Class",
            "school",
            "phone",
            "image",
            "number_of_done_exams",
            "number_of_read_notes",
            "number_of_completed_courses",
        ]
        read_only_fields = fields


class StudentProfileUpdateSerializer(serializers.Serializer):
    """Serializer for updating student profile information"""

    user = UserUpdateSerializer()
    # Student Profile fields
    Class = serializers.CharField(max_length=100, required=False)
    school = serializers.CharField(max_length=100, required=False)

    def update(self, instance, validated_data):
        # Extract user data
        user_data = validated_data.pop("user", {})

        # Update User model if user data provided
        if user_data:
            user_serializer = UserUpdateSerializer(
                instance.user, data=user_data, partial=True  # Allow partial updates
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update Profile model
        return super().update(instance, validated_data)

    def validate_Class(self, value):
        """Validate Class field with global security protection"""
        if not value:
            return value
        try:
            return SecurityValidator.validate_input(
                value, "الصف", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_school(self, value):
        """Validate school field with global security protection"""
        if not value:
            return value
        try:
            return SecurityValidator.validate_input(
                value, "المدرسة", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate(self, data):
        """Cross-field validation"""
        # Check if at least one field is provided
        if not any(data.values()):
            raise serializers.ValidationError("يجب توفير حقل واحد على الأقل للتحديث")
        return data


class PublicStudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for student profile response"""

    class Meta:
        model = StudentProfile
        fields = [
            "city",
            "image",
            "Class",
            "gender",
            "number_of_done_exams",
            "number_of_read_notes",
            "number_of_completed_courses",
        ]
        read_only_fields = fields


class OwnStudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for student profile response"""

    full_name = serializers.CharField(max_length=300, source="user.full_name")
    first_name = serializers.CharField(max_length=100, source="user.first_name")
    city = serializers.CharField(max_length=60, source="user.city")
    gender = serializers.CharField(max_length=100, source="user.gender")
    image = serializers.CharField(max_length=300, source="user.image")
    created_at = serializers.DateTimeField(source="user.created_at")
    balance = serializers.IntegerField(source="user.balance")
    email = serializers.EmailField(required=False, source="user.email")
    is_banned = serializers.BooleanField(source="user.is_banned")
    is_account_confirmed = serializers.BooleanField(source="user.is_account_confirmed")
    phone = serializers.CharField(max_length=12, source="user.phone")
    account_type = serializers.CharField(max_length=100, source="user.account_type")
    class Meta:
        model = StudentProfile
        fields = [
            "full_name",
            "first_name",
            "city",
            "account_type",
            "gender",
            "image",
            "created_at",
            "balance",
            "email",
            "is_banned",
            "phone",
            "is_account_confirmed",
            "Class",
            "number_of_done_exams",
            "number_of_read_notes",
            "number_of_completed_courses",
        ]
        read_only_fields = fields
