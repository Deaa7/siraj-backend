from rest_framework import serializers
from .models import ExamAppTracking


class ExamAppTrackingCardsSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(source='publisher_id.full_name')
    publisher_id = serializers.CharField(source='publisher_id.uuid')
    name = serializers.CharField(source='exam_id.name')
    subject_name = serializers.CharField(source='exam_id.subject_name')
    level = serializers.CharField(source='exam_id.level')
    Class = serializers.CharField(source='exam_id.Class')
    number_of_questions = serializers.IntegerField(source='exam_id.number_of_questions')
    content_public_id = serializers.CharField(source='exam_id.public_id')

    class Meta:
        model = ExamAppTracking
        fields = [
            'publisher_name',
            'publisher_id',
            'name',
            'subject_name',
            'level',
            'Class',
            'number_of_questions',
            'number_of_apps',
            'result_of_first_app',
            'result_of_last_app',
            'highest_score',
            'lowest_score',
            'time_of_first_app',
            'shortest_time',
            'result_average',
            'content_public_id',
            'last_app_date',
            'created_at',
        ]

