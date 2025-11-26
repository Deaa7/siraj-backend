from rest_framework import serializers

from .models import StudentSubjectTracking


class StudentSubjectTrackingSerializer(serializers.ModelSerializer):
    student_public_id = serializers.CharField(source="student_id.public_id", read_only=True)

    class Meta:
        model = StudentSubjectTracking
        fields = [
            "Class",
            "subject_name",
            "number_of_exams",
            "number_of_notes",
            "number_of_courses",
        ]

