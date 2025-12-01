from rest_framework import serializers

from .models import Comment
from utils.validators import CommonValidators


CONTENT_TYPES = {"exam", "note", "course", "post", "comment"}


class CommentCreateSerializer(serializers.Serializer):
    content_type = serializers.ChoiceField(choices=[(c, c) for c in CONTENT_TYPES])
    content_public_id = serializers.CharField(max_length=40)
    comment_text = serializers.CharField(max_length=1000)

    def validate_comment_text(self, value):
        return CommonValidators.validate_text_field(
            value, field_name="نص التعليق", max_length=1000
        )


class CommentUpdateSerializer(serializers.Serializer):
    comment_text = serializers.CharField(max_length=1000, required=False)

    def validate_comment_text(self, value):
        if value is None:
            return value
        return CommonValidators.validate_text_field(
            value, field_name="نص التعليق", max_length=1000
        )


class CommentDetailSerializer(serializers.ModelSerializer):
    user_public_id = serializers.CharField(source="user_id.uuid")
    user_full_name = serializers.SerializerMethodField(method_name="get_user_name")
    user_gender = serializers.CharField(source="user_id.gender")
    user_account_type = serializers.CharField(source="user_id.account_type")
    user_image = serializers.CharField(source="user_id.image", allow_blank=True)
    content_type = serializers.SerializerMethodField()
    content_public_id = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "public_id",
            "comment_text",
            "number_of_replies",
            "created_at",
            "user_public_id",
            "user_full_name",
            "user_account_type",    
            "user_image",
            "content_type",
            "content_public_id",
            "user_gender",
        ]

    def get_user_name(self, obj: Comment):
        user = obj.user_id
        if user.account_type == "teacher":
            prefix = "الاستاذ " if user.gender == "M" else "الآنسة "
            return f"{prefix}{user.full_name or user.first_name}"
        if user.account_type == "team"  or user.account_type == "admin":
            return f"فريق {user.team_name or user.full_name}"
        if user.account_type == "admin":
            return user.full_name or user.username
       
        if user.account_type == "student":
            return f"الطالب " if user.gender == "M" else "الطالبة " + (user.full_name or user.first_name)
        
        return user.full_name or user.username
       

    def _get_content_object(self, obj: Comment):
        return (
            obj.exam_id
            or obj.note_id
            or obj.course_id
            or obj.post_id
            or obj.comment_id
        )

    def get_content_type(self, obj: Comment):
        if obj.exam_id:
            return "exam"
        if obj.note_id:
            return "note"
        if obj.course_id:
            return "course"
        if obj.post_id:
            return "post"
        if obj.comment_id:
            return "comment"
        return None

    def get_content_public_id(self, obj: Comment):
        content = self._get_content_object(obj)
        if content:
            return getattr(content, "public_id", None) or getattr(content, "id", None)
        return None


class CommentListSerializer(CommentDetailSerializer):
    class Meta(CommentDetailSerializer.Meta):
        fields = CommentDetailSerializer.Meta.fields