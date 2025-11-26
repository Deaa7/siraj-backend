from rest_framework import serializers

from .models import PublisherVerificationRequests


class PublisherVerificationRequestSerializer(serializers.ModelSerializer):
    publisher_public_id = serializers.SerializerMethodField()
    publisher_name = serializers.SerializerMethodField()

    class Meta:
        model = PublisherVerificationRequests
        fields = [
            "public_id",
            "name",
            "phone",
            "email",
            "image1",
            "image2",
            "status",
            "processed_at",
            "created_at",
            "publisher_public_id",
            "publisher_name",
        ]

    def get_publisher_public_id(self, obj):
        publisher = getattr(obj, "publisher_id", None)
        if publisher and getattr(publisher, "uuid", None):
            return str(publisher.uuid)
        return None

    def get_publisher_name(self, obj):
        publisher = getattr(obj, "publisher_id", None)
        if publisher and getattr(publisher, "full_name", None):
            return publisher.full_name
        return None



class CreatePublisherVerificationRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PublisherVerificationRequests
        fields = [
            "name",
            "phone",
            "email",
            "image1",
            "image2",
        ]

