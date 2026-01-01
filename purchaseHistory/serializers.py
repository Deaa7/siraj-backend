from rest_framework import serializers

from .models import PurchaseHistory


class PurchaseHistoryDashboardSerializer(serializers.ModelSerializer):

    student_public_id = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseHistory
        fields = [
            "public_id",
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

class AdminPurchaseHistorySerializer(serializers.ModelSerializer):

    student_public_id = serializers.CharField(source='student_id.uuid' , required = False , allow_null=True , allow_blank=True)
    publisher_public_id = serializers.CharField(source='publisher_id.uuid' , required = False , allow_null=True , allow_blank=True)
    publisher_name = serializers.CharField(source='publisher_id.full_name' , required = False , allow_null=True , allow_blank=True)

    class Meta:
        model = PurchaseHistory
        fields = [
            "public_id",
            "content_name",
            "content_subject_name",
            "content_type",
            "content_class",
            "price",
            "purchase_date",
            "owner_profit",
            "discount_code",
            
            "student_public_id",
            "student_name",
            "student_city",
            "publisher_public_id",
            "publisher_name",
        ]



