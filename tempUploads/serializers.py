



from  .models import TempUpload
from rest_framework import serializers


class TempUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempUpload
        fields = ['name', 'expiration_date']