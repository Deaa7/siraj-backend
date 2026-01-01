from rest_framework import serializers
from .models import Lessons
from videos.models import Videos
 

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lessons
        fields = [
            "course_id",
            "lesson_type",
            "content_public_id",
        ]
 
        
class UpdateLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lessons
        fields = [
            "lesson_type",
            "content_public_id",
        ]
        
class GetLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lessons
        fields = [
            "public_id",
            "lesson_type",
            "content_public_id",
        ]
        
        
class GetLessonDetailsForEditSerializer(serializers.ModelSerializer):
    content_public_id = serializers.SerializerMethodField("get_content_public_id")
    name = serializers.SerializerMethodField("get_name")
    explanation = serializers.SerializerMethodField("get_explanation")
    def get_content_public_id(self, obj):
        if obj.lesson_type == "video":
            video = Videos.objects.get(public_id=obj.content_public_id)
            return video.url
        return obj.content_public_id
    def get_name(self, obj):
        if obj.lesson_type == "video":
            video = Videos.objects.get(public_id=obj.content_public_id)
            return video.name
        return ""
    def get_explanation(self, obj):
        if obj.lesson_type == "video":
            video = Videos.objects.get(public_id=obj.content_public_id)
            return video.explanation
        return ""
    class Meta:
        model = Lessons
        fields = [
            "public_id",
            "explanation",
            "lesson_type",
            "content_public_id",
            "name",
        ]