from rest_framework import serializers

from .models import StudentSavedElements


class StudentSavedElementSerializer(serializers.ModelSerializer):

    Class = serializers.SerializerMethodField( method_name="get_Class")
    subject_name = serializers.SerializerMethodField( method_name="get_subject_name")
    name = serializers.SerializerMethodField( method_name="get_name")
    price = serializers.SerializerMethodField( method_name="get_price")
    publisher_public_id = serializers.SerializerMethodField( method_name="get_publisher_public_id")
    content_public_id = serializers.SerializerMethodField( method_name="get_content_public_id")
    description = serializers.SerializerMethodField( method_name="get_description")
    level = serializers.SerializerMethodField( method_name="get_level")
    
    class Meta:
        model = StudentSavedElements
        fields = [
            "public_id",
            "type",
            "Class",
            "subject_name",
            "name",
            "price",
            "publisher_public_id",
            "content_public_id",
            "description",
            "level",
        ]

    def get_Class(self, obj):
        if obj.type == "exam":
            return obj.exam_id.Class
        elif obj.type == "note":
            return obj.note_id.Class
        elif obj.type == "course":
            return obj.course_id.Class
        
    def get_subject_name(self, obj):
        if obj.type == "exam":
            return obj.exam_id.subject_name
        elif obj.type == "note":
            return obj.note_id.subject_name
        elif obj.type == "course":
            return obj.course_id.subject_name
        
    def get_name(self, obj):
        if obj.type == "exam":
            return obj.exam_id.name
        elif obj.type == "note":
            return obj.note_id.name
        elif obj.type == "course":
            return obj.course_id.name
        
    def get_price(self, obj):
        if obj.type == "exam":
            return obj.exam_id.price
        elif obj.type == "note":
            return obj.note_id.price
        elif obj.type == "course":
            return obj.course_id.price
        
    def get_publisher_public_id(self, obj):
        if obj.type == "exam":
            return obj.exam_id.publisher_id.public_id
        elif obj.type == "note":
            return obj.note_id.publisher_id.public_id   
        elif obj.type == "course":
            return obj.course_id.publisher_id.public_id
        
    def get_content_public_id(self, obj):
        if obj.type == "exam":
            return obj.exam_id.public_id
        elif obj.type == "note":
            return obj.note_id.public_id
        elif obj.type == "course":
            return obj.course_id.public_id
    def get_description(self, obj):
        if obj.type == "exam":
            return obj.exam_id.description
        elif obj.type == "note":
            return obj.note_id.description
        elif obj.type == "course":
            return obj.course_id.description
    def get_level(self, obj):
        if obj.type == "exam":
            return obj.exam_id.level
        elif obj.type == "note":
            return obj.note_id.level
        elif obj.type == "course":
            return obj.course_id.level