from rest_framework import serializers

from .models import Notifications


class NotificationListSerializer(serializers.ModelSerializer):
    receiver_public_id = serializers.SerializerMethodField()

    class Meta:
        model = Notifications
        fields = [
            "public_id",
            "receiver_public_id",
            "source_type",
            "source_id",
            "title",
            "content",
            "read",
            "created_at",
        ]

    def get_receiver_public_id(self, obj):
        receiver = getattr(obj, "receiver_id", None)
        if receiver and getattr(receiver, "uuid", None):
            return str(receiver.uuid)
        return None



