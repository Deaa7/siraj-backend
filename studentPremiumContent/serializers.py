from rest_framework import serializers

from .models import StudentPremiumContent


class StudentPremiumContentCardSerializer(serializers.ModelSerializer):
    content_public_id = serializers.SerializerMethodField()
    content_name = serializers.SerializerMethodField()
    Class = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    publisher_name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    publisher_public_id = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentPremiumContent
        fields = [
            "type",
            "content_public_id",
            "content_name",
            "Class",
            "description",
            "publisher_name",
            "price",
            "level",
            "publisher_public_id",
            "subject_name",
        ]

    def _get_content_instance(self, obj):
        if obj.type == "exam":
            return getattr(obj, "exam_id", None)
        if obj.type == "note":
            return getattr(obj, "note_id", None)
        if obj.type == "course":
            return getattr(obj, "course_id", None)
        return None

    def get_content_public_id(self, obj):
        if obj.content_public_id:
            return obj.content_public_id
        content = self._get_content_instance(obj)
        if content and getattr(content, "public_id", None):
            return content.public_id
        return None

    def get_content_name(self, obj):
        content = self._get_content_instance(obj)
        if content:
            return getattr(content, "name", None)
        return None

    def get_Class(self, obj):
        content = self._get_content_instance(obj)
        if content:
            return getattr(content, "Class", None)
        return None

    def get_description(self, obj):
        content = self._get_content_instance(obj)
        if content:
            return getattr(content, "description", None)
        return None

    def get_publisher_name(self, obj):
        
        publisher = getattr(obj, "publisher_id", None)
        
        if publisher and getattr(publisher, "full_name", None):
            return publisher.full_name
        
        content = self._get_content_instance(obj)
        
        if content:
            publisher = getattr(content, "publisher_id", None)
        
            if publisher and getattr(publisher, "full_name", None):
                return publisher.full_name
        
        return None

    def get_price(self, obj):
        content = self._get_content_instance(obj)
        if content and getattr(content, "price", None) is not None:
            return str(content.price)
        return None

    def get_level(self, obj):
        content = self._get_content_instance(obj)
        if content:
            return getattr(content, "level", None)
        return None

    def get_publisher_public_id(self, obj):
        publisher = getattr(obj, "publisher_id", None)
        if publisher and getattr(publisher, "uuid", None):
            return str(publisher.uuid)
        content = self._get_content_instance(obj)
        if content:
            publisher = getattr(content, "publisher_id", None)
            if publisher and getattr(publisher, "uuid", None):
                return str(publisher.uuid)
        return None

    def get_subject_name(self, obj):
        content = self._get_content_instance(obj)
        if content:
            return getattr(content, "subject_name", None)
        return None

