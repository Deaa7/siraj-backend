from rest_framework import serializers
from .models import Unit
from utils.security import SecurityValidator
from django.core.exceptions import ValidationError
from Constants import CLASSES_ARRAY, SUBJECT_NAMES_ARRAY


class UnitListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing units - only returns name and slug
    """
    class Meta:
        model = Unit
        fields = ['name', 'public_id']


class UnitCRUDSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating units
    """
    class Meta:
        model = Unit
        fields = [
            'name',
            'description',
            'Class',
            'subject_name',
        ]

    def validate_name(self, value):
        """Validate name with global security protection"""
        if not value:
            raise serializers.ValidationError("اسم الوحدة مطلوب")

        try:
            return SecurityValidator.validate_input(
                value, "اسم الوحدة", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_description(self, value):
        """Validate description with global security protection"""
        if not value:
            return value

        try:
            return SecurityValidator.validate_input(
                value, "وصف الوحدة", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    def validate_Class(self, value):
        """Validate Class"""
        if value not in CLASSES_ARRAY:
            raise serializers.ValidationError("الصف غير متوفر")
        return value

    def validate_subject_name(self, value):
        """Validate subject_name"""
        if value not in SUBJECT_NAMES_ARRAY:
            raise serializers.ValidationError("المادة غير متوفرة")
        return value


class UnitDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for unit details - returns all fields
    """
    class Meta:
        model = Unit
        fields = [
            'public_id',
            'name',
            'slug',
            'description',
            'Class',
            'subject_name',
            'created_at',
            'updated_at',
        ]

