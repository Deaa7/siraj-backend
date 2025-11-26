from rest_framework import serializers
from .models import TeacherProfile
from utils.security import SecurityValidator
from django.core.exceptions import ValidationError
from Constants import CLASSES, SUBJECT_NAMES
from users.serializers import UserUpdateSerializer
from users.models import User


class TeacherProfileUpdateSerializer(serializers.Serializer):
    """Serializer for updating teacher profile information"""

    user = UserUpdateSerializer()
    # Teacher Profile fields
    Class = serializers.CharField(max_length=100, required=False)
    studying_subjects = serializers.CharField(max_length=100, required=False)
    university = serializers.CharField(max_length=100, required=False)
    address = serializers.CharField(max_length=500, required=False, allow_blank=True)
    bio = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    years_of_experience = serializers.IntegerField(
        required=False, min_value=0, max_value=50
    )

    # Social media links
    telegram_link = serializers.URLField(
        max_length=200, required=False, allow_blank=True
    )
    whatsapp_link = serializers.URLField(
        max_length=200, required=False, allow_blank=True
    )
    instagram_link = serializers.URLField(
        max_length=200, required=False, allow_blank=True
    )
    facebook_link = serializers.URLField(
        max_length=200, required=False, allow_blank=True
    )
    x_link = serializers.URLField(max_length=200, required=False, allow_blank=True)
    linkedin_link = serializers.URLField(
        max_length=200, required=False, allow_blank=True
    )

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
        if value not in CLASSES:
            raise serializers.ValidationError("الصف يجب أن يكون من القائمة")
        return value

    def validate_studying_subjects(self, value):
        """Validate studying subjects with global security protection"""
        if not value:
            return value
        if value not in SUBJECT_NAMES:
            raise serializers.ValidationError("المواد الدراسية يجب أن يكون من القائمة")
        return value

    def validate_university(self, value):
        """Validate university with global security protection"""
        if not value:
            return value

        try:
            return SecurityValidator.validate_input(
                value, "الجامعة", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_address(self, value):
        """Validate address with global security protection"""
        if not value:
            return value

        try:
            return SecurityValidator.validate_input(
                value, "العنوان", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_bio(self, value):
        """Validate bio with global security protection"""
        if not value:
            return value

        try:
            return SecurityValidator.validate_input(
                value, "النبذة الشخصية", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_years_of_experience(self, value):
        """Validate years of experience"""
        if value is None:
            return value

        if value < 0:
            raise serializers.ValidationError("سنوات الخبرة لا يمكن أن تكون سالبة")

        if value > 50:
            raise serializers.ValidationError(
                "سنوات الخبرة لا يمكن أن تكون أكثر من 50 سنة"
            )

        return value

    def validate_telegram_link(self, value):
        """Validate telegram link"""
        if not value:
            return value

        # Check if it's a valid social media URL
        if not any(domain in value.lower() for domain in ["telegram.me", "t.me"]):
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً للتليجرام")

        return value

    def validate_whatsapp_link(self, value):
        """Validate whatsapp link"""
        if not value:
            return value

        # Check if it's a valid social media URL
        if not any(domain in value.lower() for domain in ["wa.me", "whatsapp.com"]):
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً للواتساب")

        return value

    def validate_instagram_link(self, value):
        """Validate instagram link"""
        if not value:
            return value

        # Check if it's a valid social media URL
        if "instagram.com" not in value.lower():
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً للانستغرام")

        return value

    def validate_facebook_link(self, value):
        """Validate facebook link"""
        if not value:
            return value

        # Check if it's a valid social media URL
        if "facebook.com" not in value.lower():
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً للفيسبوك")

        return value

    def validate_x_link(self, value):
        """Validate X (Twitter) link"""
        if not value:
            return value

        # Check if it's a valid social media URL
        if not any(domain in value.lower() for domain in ["twitter.com", "x.com"]):
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً لإكس (تويتر)")

        return value

    def validate_linkedin_link(self, value):
        """Validate linkedin link"""
        if not value:
            return value

        # Check if it's a valid social media URL
        if "linkedin.com" not in value.lower():
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً للينكد إن")

        return value

    def validate(self, data):
        """Cross-field validation"""
        # Check if at least one field is provided
        if not any(data.values()):
            raise serializers.ValidationError("يجب توفير حقل واحد على الأقل للتحديث")

        return data


class PublicTeacherProfileSerializer(serializers.ModelSerializer):
    """Serializer for teacher profile response"""
    full_name = serializers.CharField(max_length=300, source="user.full_name")
    city = serializers.CharField(max_length=60, source="user.city")
    gender = serializers.CharField(max_length=100, source="user.gender")
    image = serializers.CharField(max_length=300, source="user.image")
    created_at = serializers.DateTimeField(source="user.created_at")
    account_type = serializers.CharField(max_length=100, source="user.account_type")
    
    class Meta:
        model = TeacherProfile
        fields = [
            "full_name",
            "city",
            "gender",
            "image",
            "created_at",
            "account_type",
            "studying_subjects",
            "university",
            "address",
            "Class",
            "number_of_exams",
            "number_of_notes",
            "number_of_courses",
            "number_of_followers",
            "telegram_link",
            "whatsapp_link",
            "instagram_link",
            "facebook_link",
            "x_link",
            "linkedin_link",
            "bio",
            "years_of_experience",
        ]
        read_only_fields = fields


class OwnTeacherProfileSerializer(serializers.ModelSerializer):
    """Serializer for own teacher profile response"""

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
    account_type = serializers.CharField(max_length=100, source="user.account_type")
    uuid = serializers.UUIDField(source="user.uuid")
    class Meta:
        model = TeacherProfile
        fields = [
            "full_name",
            "first_name",
            "city",
            "gender",
            "image",
            "created_at",
            "balance",
            "email",
            "is_banned",
            "is_account_confirmed",
            "account_type",
            "uuid",
            "studying_subjects",
            "university",
            "address",
            "Class",
            "number_of_exams",
            "number_of_notes",
            "number_of_courses",
            "number_of_followers",
            "telegram_link",
            "whatsapp_link",
            "instagram_link",
            "facebook_link",
            "x_link",
            "linkedin_link",
            "verified",
            "bio",
            "years_of_experience",
        ]
        read_only_fields = fields


class TeacherPreviewSerializer(serializers.ModelSerializer):
    """Serializer for teacher preview cards"""
    full_name = serializers.CharField(max_length=300, source="user.full_name")
    city = serializers.CharField(max_length=60, source="user.city")
    gender = serializers.CharField(max_length=100, source="user.gender")
    image = serializers.CharField(max_length=300, source="user.image")
    created_at = serializers.DateTimeField(source="user.created_at")
    account_type = serializers.CharField(max_length=100, source="user.account_type")
    uuid = serializers.UUIDField(source="user.uuid")
    class Meta:
        model = TeacherProfile
        fields = [
            "full_name",
            "city",
            "gender",
            "image",
            "created_at",
            "account_type",
            "uuid",
            "Class",
            "studying_subjects",
            "address",
            "university",
            "years_of_experience",
            "number_of_exams",
            "number_of_notes",
            "number_of_courses",
            "number_of_followers",
        ]
