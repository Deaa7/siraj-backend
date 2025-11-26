from rest_framework import serializers
from utils.validators import CommonValidators


class VideoSerializer(serializers.Serializer):

    # video_file = serializers.FileField(required=True)
    video_file_path = serializers.CharField(required=True , max_length=400)
    video_explanation = serializers.CharField(max_length=40000)

    def validate_video_explanation(self, value):
        return CommonValidators.validate_text_field(value, field_name="Video explanation", max_length=40000)
    
    # def validate_video_file(self, value):
    #     # Maximum file size: 2 GB (in bytes)
 
    #     if not value:
    #         raise serializers.ValidationError("ملف الفيديو مطلوب")
        
    #     # Check file size
    #     if value.size > VIDEO_MAX_FILE_SIZE:
    #         size_mb = value.size / (1024 * 1024)
    #         raise serializers.ValidationError(
    #             f"حجم الملف ({size_mb:.2f} MB) يتجاوز الحد الأقصى المسموح به (2 GB)"
    #         )
        
    #     # Check file extension
    #     file_name = value.name.lower()
        
    #     if not any(file_name.endswith(ext) for ext in VIDEO_ALLOWED_EXTENSIONS):
    #         raise serializers.ValidationError(
    #             f"صيغة الملف غير مدعومة. الصيغ المدعومة: {', '.join(VIDEO_ALLOWED_EXTENSIONS)}"
    #         )
        
    #     # Check content type if available
    #     if hasattr(value, 'content_type') and value.content_type:
    #         if value.content_type not in VIDEO_ALLOWED_FORMATS:
    #             raise serializers.ValidationError(
    #                 f"نوع الملف ({value.content_type}) غير مدعوم. يجب أن يكون ملف فيديو"
    #             )
        
    #     return upload_file_to_bucket(value)