from rest_framework import serializers
from .models import TeamProfile
from rest_framework import serializers
from utils.security import SecurityValidator
from django.core.exceptions import ValidationError
# from users.serializers import UserUpdateSerializer
from users.models import User
from utils.validators import CommonValidators
from Constants import  CITIES_ARRAY
class TeamUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "city",
            "image",
            "phone",
            "team_name",
        ]
        extra_kwargs = {
            'phone': {'validators': []}  # Disable default unique validator
        }
        
    def validate_first_name(self, value):
        """Validate first name"""
    
        if not value:
            raise serializers.ValidationError("الاسم الأول مطلوب")
        return CommonValidators.validate_arabic_text(value, "الاسم الأول")

    def validate_last_name(self, value):
        """Validate last name"""
        if not value:
            return value
        return CommonValidators.validate_arabic_text(value, "الاسم الأخير")

    def validate_team_name(self, value):
        """Validate team name"""
    
        if not value:
            raise serializers.ValidationError("اسم الفريق مطلوب")
        return CommonValidators.validate_arabic_text(value, "اسم الفريق")

    def validate_city(self, value):
        """Validate city"""
        if not value:
         raise serializers.ValidationError("المدينة مطلوبة")
        if value not in CITIES_ARRAY:
            raise serializers.ValidationError("المدينة يجب أن يكون من القائمة")
        return value
    
    def validate_phone(self, value):
        """Validate phone with global security protection"""
        if not value:
              raise serializers.ValidationError("رقم الهاتف مطلوب")
        try:
            return SecurityValidator.validate_input(
                value, "الهاتف", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))


class TeamPreviewSerializer(serializers.ModelSerializer):
    """Serializer for team profile response"""
    team_name = serializers.CharField(max_length=250, source="user.team_name")
    city = serializers.CharField(max_length=60, source="user.city")
    image = serializers.CharField(max_length=300, source="user.image")
    created_at = serializers.DateTimeField(source="user.created_at")
    account_type = serializers.CharField(max_length=100, source="user.account_type")
    uuid = serializers.UUIDField(source="user.uuid")
    
    class Meta:
        model = TeamProfile
        fields = [
            "team_name",
            "city",
            "image",
            "created_at",
            "account_type",
            "uuid",
            "number_of_exams",
            "number_of_notes",
            "number_of_courses",
            "number_of_followers",
            "address",
            "years_of_experience",
        ]
        read_only_fields = fields


class TeamProfileUpdateSerializer(serializers.Serializer):
    """Serializer for updating team profile information"""
    
    user = TeamUserUpdateSerializer()
    # team Profile fields
    address = serializers.CharField(max_length=500, required=False, allow_blank=True)
    bio = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    years_of_experience = serializers.IntegerField(required=False, min_value=0, max_value=50)

    # Social media links
    telegram_link = serializers.URLField(max_length=200, required=False, allow_blank=True)
    whatsapp_link = serializers.URLField(max_length=200, required=False, allow_blank=True)
    instagram_link = serializers.URLField(max_length=200, required=False, allow_blank=True)
    facebook_link = serializers.URLField(max_length=200, required=False, allow_blank=True)
    x_link = serializers.URLField(max_length=200, required=False, allow_blank=True)
    linkedin_link = serializers.URLField(max_length=200, required=False, allow_blank=True)
   
    def validate_address(self, value):
        """Validate address with global security protection"""
        if not value:
            return value
        try:
            return SecurityValidator.validate_input(value, "العنوان", check_sql_injection=True, check_xss=False)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
    
    def validate_bio(self, value):
        """Validate bio with global security protection"""
        if not value:
            return value
        try:
            return SecurityValidator.validate_input(value, "النبذة الشخصية", check_sql_injection=True, check_xss=False)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
    
    def validate_years_of_experience(self, value):
        """Validate years of experience"""
        if value is None:
            return value
        
        if value < 0:
            raise serializers.ValidationError("سنوات الخبرة لا يمكن أن تكون سالبة")
        
        if value > 50:
            raise serializers.ValidationError("سنوات الخبرة لا يمكن أن تكون أكثر من 50 سنة")
        
        return value
    
    def validate_telegram_link(self, value):
        """Validate telegram link"""
        if not value:
            return value
        # Check if it's a valid social media URL
        if not any(domain in value.lower() for domain in ['telegram.me', 't.me']):
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً للتليجرام")
        
        return value
    
    def validate_whatsapp_link(self, value):
        """Validate whatsapp link"""
        if not value:
            return value
        # Check if it's a valid social media URL
        if not any(domain in value.lower() for domain in ['wa.me', 'whatsapp.com']):
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً للواتساب")
        return value
    
    def validate_instagram_link(self, value):
        """Validate instagram link"""
        if not value:
            return value
        # Check if it's a valid social media URL
        if 'instagram.com' not in value.lower():
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً للانستغرام")
        return value
    
    def validate_facebook_link(self, value):
        """Validate facebook link"""
        if not value:
            return value
        # Check if it's a valid social media URL
        if 'facebook.com' not in value.lower():
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً للفيسبوك")
        return value
    
    def validate_x_link(self, value):
        """Validate X (Twitter) link"""
        if not value:
            return value
        # Check if it's a valid social media URL
        if not any(domain in value.lower() for domain in ['twitter.com', 'x.com']):
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً لإكس (تويتر)")
        return value
    
    def validate_linkedin_link(self, value):
        """Validate linkedin link"""
        if not value:
            return value
        # Check if it's a valid social media URL
        if 'linkedin.com' not in value.lower():
            raise serializers.ValidationError("يجب أن يكون الرابط صحيحاً للينكد إن")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Check if at least one field is provided
        if not any(data.values()):
            raise serializers.ValidationError("يجب توفير حقل واحد على الأقل للتحديث")
        return data
    
    def update(self, instance, validated_data):
        # Extract user data
        user_data = validated_data.pop("user", {})

        # Update User model if user data provided
        if user_data:
            user_serializer = TeamUserUpdateSerializer(
                instance.user, data=user_data, partial=True  # Allow partial updates
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

         # Update Profile model fields
        if "address" in validated_data:
            instance.address = validated_data.get("address", instance.address)
        if "bio" in validated_data:
            instance.bio = validated_data.get("bio", instance.bio)
        if "years_of_experience" in validated_data:
            instance.years_of_experience = validated_data.get("years_of_experience", instance.years_of_experience)
        if "telegram_link" in validated_data:
            instance.telegram_link = validated_data.get("telegram_link", instance.telegram_link)
        if "whatsapp_link" in validated_data:
            instance.whatsapp_link = validated_data.get("whatsapp_link", instance.whatsapp_link)
        if "instagram_link" in validated_data:
            instance.instagram_link = validated_data.get("instagram_link", instance.instagram_link)
        if "facebook_link" in validated_data:
            instance.facebook_link = validated_data.get("facebook_link", instance.facebook_link)
        if "x_link" in validated_data:
            instance.x_link = validated_data.get("x_link", instance.x_link)
        if "linkedin_link" in validated_data:
            instance.linkedin_link = validated_data.get("linkedin_link", instance.linkedin_link)
        
        instance.save()
        return instance


class PublicTeamProfileSerializer(serializers.ModelSerializer):
    """Serializer for teacher profile response"""
    team_name = serializers.CharField(max_length=250, source="user.team_name")
    city = serializers.CharField(max_length=60, source="user.city")
    image = serializers.CharField(max_length=300, source="user.image")
    created_at = serializers.DateTimeField(source="user.created_at")
    account_type = serializers.CharField(max_length=100, source="user.account_type")
    public_id = serializers.UUIDField(source="user.uuid")
    class Meta:
        model = TeamProfile
        fields = [
            "team_name",
            "city",
            "image",
            "created_at",
            "account_type",
            "public_id",
            "verified",
            "address",
            "number_of_exams",
            "number_of_notes",
            "number_of_courses",
            "number_of_followers",
            "telegram_link",
            "whatsapp_link",
            "instagram_link",
            "facebook_link",
            "x_link",
            "linkedin_link",
            "bio",
            "years_of_experience",
        ]
        read_only_fields = fields


class OwnTeamProfileSerializer(serializers.ModelSerializer):
    """Serializer for own team profile response"""

    team_name = serializers.CharField(max_length=250 , source="user.team_name")
    first_name = serializers.CharField(max_length=100 , source="user.first_name")
    last_name = serializers.CharField(max_length=100 , source="user.last_name")
    phone = serializers.CharField(max_length=100 , source="user.phone")
    city = serializers.CharField(max_length=60 , source="user.city") 
    image = serializers.CharField(max_length=300 , source="user.image")
    created_at = serializers.DateTimeField(source="user.created_at")
    balance = serializers.IntegerField(source="user.balance")
    email = serializers.EmailField(required=False, source="user.email")
    is_banned = serializers.BooleanField(source="user.is_banned")
    is_account_confirmed = serializers.BooleanField(source="user.is_account_confirmed")
    account_type = serializers.CharField(max_length=100, source="user.account_type")    
    uuid = serializers.UUIDField(source="user.uuid")
    class Meta:
        model = TeamProfile
        fields = [        
            "team_name",
            "first_name",
            "last_name",
            "phone",
            "city",
            "image",
            "created_at",
            "balance",
            "email",
            "is_banned",
            "is_account_confirmed",
            "account_type",
            "uuid",
            "address",
            "number_of_exams",
            "number_of_notes",
            "number_of_courses",
            "number_of_followers",
            "telegram_link",
            "whatsapp_link",
            "instagram_link",
            "facebook_link",
            "x_link",
            "linkedin_link",
            "verified",
            "bio",
            "years_of_experience",
            ]
        read_only_fields = fields

