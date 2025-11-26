from rest_framework import serializers
from .models import CourseStatusTracking




class CourseStatusTrackingCardsSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(source='publisher_id.full_name')
    publisher_id = serializers.CharField(source='publisher_id.uuid')
    name = serializers.CharField(source='course_id.name')
    subject_name = serializers.CharField(source='course_id.subject_name')
    level = serializers.CharField(source='course_id.level')
    Class = serializers.CharField(source='course_id.Class')
    number_of_lessons = serializers.IntegerField(source='course_id.number_of_lessons')
    content_public_id = serializers.CharField(source='course_id.public_id')
    class Meta:
        model = CourseStatusTracking
        fields = ['publisher_name',
                  'publisher_id',
                  'name',
                  'subject_name', 
                  'level',
                  'Class',
                  'number_of_lessons',
                  'content_public_id',
                  'complete',
                  'created_at',
                  'complete_date'
                  ]
    