from rest_framework import serializers
from utils.validators import CommonValidators
from .models import Videos

class VideoSerializer(serializers.Serializer):

    # video_file = serializers.FileField(required=True)
    name = serializers.CharField(required=True , max_length=400)
    explanation = serializers.CharField(max_length=40000 , required=False ,   
        allow_null=True, 
        allow_blank=True  # This is the missing piece
        )

    def validate_explanation(self, value):
        return CommonValidators.validate_text_field(value, field_name="Explanation", max_length=40000 ,allow_empty=True)
   
    def validate_name(self, value):
        return CommonValidators.validate_text_field(value, field_name="Name", max_length=500)
     
    
class CreateVideoSerializer(serializers.Serializer):
   
    name = serializers.CharField(required=True , max_length=400 )
    explanation = serializers.CharField(max_length=40000 , required=False, 
        allow_null=True, 
        allow_blank=True  # This is the missing piece
        )
    url = serializers.CharField(required=True)
    
    def validate_explanation(self, value):
        return CommonValidators.validate_text_field(value, field_name="Explanation", max_length=40000 ,allow_empty=True)
   
    def validate_name(self, value):
        return CommonValidators.validate_text_field(value, field_name="Name", max_length=500)
     
    class Meta : 
        model = Videos
        fields = ['name', 'explanation' , 'url' , 'publisher_id']
    
    def create(self, validated_data):
        return Videos.objects.create(**validated_data)