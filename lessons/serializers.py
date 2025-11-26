from rest_framework import serializers
from .models import Lessons
from utils.validators import CommonValidators

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lessons
        fields = [
            "course_id",
            "lesson_name",
            "lesson_type",
            "content_public_id",
        ]
        
    def validate_lesson_name(self, value):
        if not value:
            raise serializers.ValidationError("اسم الدرس مطلوب")
        return CommonValidators.validate_text_field(value, "اسم الدرس", max_length=300)

class GetLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lessons
        fields = [
            "public_id",
            "lesson_name",
            "lesson_type",
            "content_public_id",
        ]