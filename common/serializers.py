from rest_framework import serializers
from teacherProfile.models import TeacherProfile
from teamProfile.models import TeamProfile


class MostPopularPublisherSerializer(serializers.Serializer):
    """Serializer for most popular publisher statistics"""
    
    name = serializers.CharField()
    subject_name = serializers.CharField(allow_null=True)
    Class = serializers.CharField(allow_null=True)
    university = serializers.CharField(allow_null=True)
    city = serializers.CharField()
    address = serializers.CharField(allow_null=True)
    number_of_exams = serializers.IntegerField()
    number_of_notes = serializers.IntegerField()
    number_of_courses = serializers.IntegerField()
    number_of_followers = serializers.IntegerField()
    experience_years = serializers.IntegerField(allow_null=True)
    publisher_type = serializers.CharField()  # "teacher" or "team"
    publisher_id = serializers.CharField()  # UUID






