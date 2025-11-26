from rest_framework import serializers
from .models import NoteReadTracking


class NoteReadTrackingCardsSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(source='publisher_id.full_name')
    publisher_id = serializers.CharField(source='publisher_id.uuid')
    name = serializers.CharField(source='note_id.name')
    subject_name = serializers.CharField(source='note_id.subject_name')
    level = serializers.CharField(source='note_id.level')
    Class = serializers.CharField(source='note_id.Class')
    number_of_pages = serializers.IntegerField(source='note_id.number_of_pages')
    # note_number_of_reads = serializers.IntegerField(source='note_id.number_of_reads')
    content_public_id = serializers.CharField(source='note_id.public_id')

    class Meta:
        model = NoteReadTracking
        fields = [
            'publisher_name',
            'publisher_id',
            'name',
            'subject_name',
            'level',
            'Class',
            'number_of_pages',
            # 'note_number_of_reads',
            'number_of_reads',
            'first_read_date',
            'last_read_date',
            'content_public_id',
            'created_at',
        ]

