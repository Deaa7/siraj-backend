from rest_framework import serializers

from .models import Reports


class ReportListSerializer(serializers.ModelSerializer):
    user_public_id = serializers.SerializerMethodField()
    reported_user_public_id = serializers.SerializerMethodField()

    class Meta:
        model = Reports
        fields = [
            "public_id",
            "user_public_id",
            "full_name",
            "reported_user_public_id",
            "reported_user_full_name",
            "report_date",
            "report_description",
            "reported_content_type",
            "verified",
        ]

    def get_user_public_id(self, obj):
        user = getattr(obj, "user_id", None)
        if user and getattr(user, "uuid", None):
            return str(user.uuid)
        return None

    def get_reported_user_public_id(self, obj):
        reported_user = getattr(obj, "reported_user_id", None)
        if reported_user and getattr(reported_user, "uuid", None):
            return str(reported_user.uuid)
        return None



