from rest_framework import serializers

from .models import PurchaseHistory


class PurchaseHistoryDashboardSerializer(serializers.ModelSerializer):

    student_public_id = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseHistory
        fields = [
            "content_name",
            "content_type",
            "content_class",
            "price",
            "content_subject_name",
            "student_public_id",
            "student_name",
            "student_city",
            "purchase_date",
            "publisher_profit",
            "discount_code",
            
        ]

    def get_student_public_id(self, obj):
        student = getattr(obj, "student_id", None)
        if student and getattr(student, "uuid", None):
            return str(student.uuid)
        return None

