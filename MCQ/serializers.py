from rest_framework import serializers
from .models import MCQ


class MCQSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQ
        fields = [
            "exam",
            "question",
            "question_image",
            "option_A",
            "option_B",
            "option_C",
            "option_D",
            "option_E",
            "right_answer",
            "explanation",
            "is_arabic",
        ]
        