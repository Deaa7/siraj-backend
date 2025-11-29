from rest_framework import serializers
from django.core.exceptions import ValidationError

from .models import User
from teacherProfile.models import TeacherProfile
from studentProfile.models import StudentProfile
from teamProfile.models import TeamProfile
from publisherOffers.models import PublisherOffers


from studentSubjectTracking.models import StudentSubjectTracking
from Constants import GENDERS, CITIES
from Constants import (
    SUBJECT_NAMES_ARRAY,
    CLASSES_ARRAY,
    SUBJECT_NAMES_DICT,
    CLASSES_DICT,
)

# Import global security utilities
from utils.security import SecurityValidator
from utils.validators import CommonValidators
from publisherPlans.models import PublisherPlans
from django.utils import timezone
from datetime import timedelta


# this is helper serializer for updating teacher/student profile , used as refrence for the user fields
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "gender",
            "city",
            "image",
        ]  # User fields to update

    def validate_first_name(self, value):
        """Validate first name"""
        if value is None:
            return value
        return CommonValidators.validate_arabic_text(value, "الاسم الأول")

    def validate_last_name(self, value):
        """Validate last name"""
        if value is None:
            return value
        return CommonValidators.validate_arabic_text(value, "الاسم الأخير")

    def validate_gender(self, value):
        """Validate gender"""
        if value is None:
            return value
        if value not in GENDERS:
            raise serializers.ValidationError("الجنس يجب أن يكون من القائمة")
        return value

    def validate_city(self, value):
        """Validate city"""
        if value is None:
            return value
        if value not in CITIES:
            raise serializers.ValidationError("المدينة يجب أن يكون من القائمة")
        return value

    def validate_phone(self, value):
        """Validate phone with global security protection"""
        if not value:
            return value
        try:
            return SecurityValidator.validate_input(
                value, "الهاتف", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))


######################################


# this is helper serializer for TeacherRegistrationSerializer
class TeacherRegistrationHelperSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ["studying_subjects", "Class"]

    def validate_studying_subjects(self, value):
        """Validate studying subjects"""

        if not value:
            raise serializers.ValidationError("المواد الدراسية مطلوبة")
        if not value in SUBJECT_NAMES_ARRAY:
            raise serializers.ValidationError("المواد الدراسية يجب أن يكون من القائمة")
        return value

    def validate_Class(self, value):
        """Validate Class"""
        if not value:
            raise serializers.ValidationError("الصف مطلوب")
        if not value in CLASSES_ARRAY:
            raise serializers.ValidationError("الصف يجب أن يكون من القائمة")
        return value


##################################


# this is the main serializer for teacher registration
class TeacherRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for teacher registration"""

    profile = TeacherRegistrationHelperSerializer()
    # write_only means that the field will not be included in the response
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "profile",
            "username",
            "email",
            "account_type",
            "phone",
            "city",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "gender",
        ]
        # Disable default UniqueValidator messages (English) and rely on custom Arabic validators
        extra_kwargs = {
            "username": {"validators": []},
            "email": {"validators": []},
            "phone": {"validators": []},
        }

    def validate_username(self, value):
        """Validate username with global security protection"""

        secure_value = CommonValidators.validate_username(value, "اسم المستخدم")
        
        if User.objects.filter(username=secure_value).exists():
            raise serializers.ValidationError(" اسم المستخدم مسجل مسبقاً")

        return secure_value

    def validate_email(self, value):
        """Validate phone with global security protection"""
        secure_value = CommonValidators.validate_email_field(value, "البريد الإلكتروني")
        
        if User.objects.filter(email=secure_value).exists():
            raise serializers.ValidationError("البريد الإلكتروني مسجل مسبقاً")
        return secure_value

    def validate_password(self, value):
        """Validate password with global security protection"""
        return CommonValidators.validate_password(value, "كلمة المرور")
 
    def validate_phone(self, value):
      """Validate phone with global security protection"""
      secure_value = CommonValidators.validate_phone(value, "الهاتف")
      if User.objects.filter(phone=secure_value).exists():
            raise serializers.ValidationError("رقم الهاتف مسجل مسبقاً")
      return secure_value
    
    def validate(self, data):
        """Cross-field validation"""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                "كلمة المرور وتأكيد كلمة المرور يجب أن يكونا متطابقين"
            )
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")

        bio = ""
        studying_subject = profile_data["studying_subjects"]
        class_level = profile_data["Class"]
        if validated_data.get("gender") == "M":
            bio = f"استاذ متخصص في مادة {SUBJECT_NAMES_DICT[studying_subject]} للصف {CLASSES_DICT[class_level]}"
        else:
            bio = f"آنسة متخصصة في مادة {SUBJECT_NAMES_DICT[studying_subject]} للصف {CLASSES_DICT[class_level]}"

        profile_data["bio"] = bio
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        # Create User
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Create Profile
        TeacherProfile.objects.create(user=user, **profile_data)

        free_offer = PublisherOffers.objects.filter(
            offer_price=0, offer_for="teacher"
        ).first()

        PublisherPlans.objects.create(
            user=user,
            offer=free_offer,
            activation_date=timezone.now(),
        )

        return user


######################################

# this is helper serializer for StudentRegistrationSerializer
class StudentRegistrationHelperSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ["Class"]

    def validate_Class(self, value):
        """Validate Class"""
        if not value:
            raise serializers.ValidationError("الصف مطلوب")
        if value not in CLASSES_ARRAY:
            raise serializers.ValidationError("الصف يجب أن يكون من القائمة")
        return value


######################################


# this is the main serializer for student registration
class StudentRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for student registration"""

    profile = StudentRegistrationHelperSerializer()
    # write_only means that the field will not be included in the response
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "profile",
            "username",
            "email",
            "account_type",
            "phone",
            "city",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "gender",
        ]
        # Disable DRF UniqueValidator default messages, rely on Arabic custom validators
        extra_kwargs = {
            "username": {"validators": []},
            "email": {"validators": []},
            "phone": {"validators": []},
        }

    def validate_username(self, value):
        """Validate username with global security protection"""
        secure_value = CommonValidators.validate_username(value, "اسم المستخدم")
        if User.objects.filter(username=secure_value).exists():
            raise serializers.ValidationError(" اسم المستخدم مسجل مسبقاً")

        return secure_value

    def validate_email(self, value):
        """Validate email with global security protection"""
        secure_value = CommonValidators.validate_email_field(value, "البريد الإلكتروني")

        if User.objects.filter(email=secure_value).exists():
            raise serializers.ValidationError("البريد الإلكتروني مسجل مسبقاً")
        return secure_value
    
    def validate_phone(self, value):
        """Validate phone with global security protection"""
        secure_value = CommonValidators.validate_phone(value, "الهاتف")
        if User.objects.filter(phone=secure_value).exists():
            raise serializers.ValidationError("رقم الهاتف مسجل مسبقاً")
        return secure_value

    def validate_password(self, value):
        """Validate password with global security protection"""
        return CommonValidators.validate_password(value, "كلمة المرور")

    def validate(self, data):
        """Cross-field validation"""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                "كلمة المرور وتأكيد كلمة المرور يجب أن يكونا متطابقين"
            )
        return data

    def create(self, validated_data):

        profile_data = validated_data.pop("profile")

        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        # Create User
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Create Profile
        student_profile = StudentProfile.objects.create(user=user, **profile_data)

        # Create subject tracking records
        student_class = profile_data.get("Class", student_profile.Class)
        for subject_value in SUBJECT_NAMES_ARRAY:
            StudentSubjectTracking.objects.create(
                student_id=user,
                Class=student_class,
                subject_name=subject_value,
            )

        return user


######################################


class TeamRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for team registration"""

    # write_only means that the field will not be included in the response
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "account_type",
            "phone",
            "city",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "team_name",
        ]
        # Disable DRF UniqueValidator default messages, rely on Arabic custom validators
        extra_kwargs = {
            "username": {"validators": []},
            "email": {"validators": []},
            "team_name": {"validators": []},
            "phone": {"validators": []},
        }

    def validate_username(self, value):
        """Validate username with global security protection"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(" اسم المستخدم مسجل مسبقاً")

        return CommonValidators.validate_username(value, "اسم المستخدم")

    def validate_team_name(self, value):
        """Validate username with global security protection"""
        if User.objects.filter(team_name=value).exists():
            raise serializers.ValidationError(" اسم الفريق مسجل مسبقاً")
        return CommonValidators.validate_team_name(value, "اسم الفريق")
    
    def validate_email(self, value):
        """Validate email with global security protection"""
        secure_value = CommonValidators.validate_email_field(value, "البريد الإلكتروني")
        if User.objects.filter(email=secure_value).exists():
            raise serializers.ValidationError("البريد الإلكتروني مسجل مسبقاً")
        return secure_value
    
    def validate_phone(self, value):
        """Validate phone with global security protection"""
        secure_value = CommonValidators.validate_phone(value, "الهاتف")
        if User.objects.filter(phone=secure_value).exists():
            raise serializers.ValidationError("رقم الهاتف مسجل مسبقاً")
        return secure_value

    def validate_password(self, value):
        """Validate password with global security protection"""
        return CommonValidators.validate_password(value, "كلمة المرور")

    def validate(self, data):
        """Cross-field validation"""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                "كلمة المرور وتأكيد كلمة المرور يجب أن يكونا متطابقين"
            )
        return data

    def create(self, validated_data):

        profile_data = {"bio": f"فريق {validated_data.get('team_name')}"}

        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        # Create User
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Create Profile
        TeamProfile.objects.create(user=user, **profile_data)
        free_offer = PublisherOffers.objects.filter(
            offer_price=0, offer_for="team"
        ).first()

        PublisherPlans.objects.create(
            user=user,
            offer=free_offer,
            activation_date=timezone.now(),
        )

        return user

######################################


class LoginSerializer(serializers.Serializer):
    """Serializer for login"""

    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, required=True, write_only=True)

    def validate_username(self, value):
        if value.startswith("deleted_"):
            raise serializers.ValidationError("اسم المستخدم غير مسجل في النظام")
        """Validate username with global security protection"""
        return SecurityValidator.validate_username_field(value, "اسم المستخدم")

    def validate_password(self, value):
        """Validate password with global security protection"""
        return SecurityValidator.validate_password_field(value, "كلمة المرور")


class AdminLoginSerializer(serializers.Serializer):
    """Serializer for admin login"""

    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, required=True, write_only=True)

    def validate_username(self, value):
        """Validate username with global security protection"""
        return SecurityValidator.validate_username_field(value, "اسم المستخدم")

    def validate_password(self, value):
        """Validate password with global security protection"""
        return SecurityValidator.validate_password_field(value, "كلمة المرور")


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for refresh token"""

    refresh = serializers.CharField(required=True)

    def validate_refresh(self, value):
        """Validate refresh token with global security protection"""
        return SecurityValidator.validate_input(
            value, "رمز التحديث", check_sql_injection=True, check_xss=False
        )


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for reset password request"""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate email with global security protection"""
        validated_email = CommonValidators.validate_email_field(
            value, "البريد الإلكتروني"
        )

        # Check if email exists in database
        if not User.objects.filter(email=validated_email).exists():
            raise serializers.ValidationError("البريد الإلكتروني غير مسجل في النظام")

        return validated_email


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation with OTP"""

    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(max_length=4, required=True)
    new_password = serializers.CharField(max_length=128, required=True, write_only=True)

    def validate_email(self, value):
        """Validate email with global security protection"""
        validated_email = CommonValidators.validate_email_field(
            value, "البريد الإلكتروني"
        )

        # Check if email exists in database
        if not User.objects.filter(email=validated_email).exists():
            raise serializers.ValidationError("البريد الإلكتروني غير مسجل في النظام")

        return validated_email

    def validate_otp_code(self, value):
        """Validate OTP code with global security protection"""
        if not value:
            raise serializers.ValidationError("رمز التحقق مطلوب")

        # Security validation
        try:
            value = SecurityValidator.validate_input(
                value, "رمز التحقق", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        # Check if OTP is 4 digits
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("رمز التحقق يجب أن يكون 4 أرقام")

        return value

    def validate_new_password(self, value):
        """Validate new password with global security protection"""
        return CommonValidators.validate_password(value, "كلمة المرور الجديدة")

    def validate(self, data):
        """Cross-field validation"""
        new_password = data.get("new_password")

        return data


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification with OTP"""

    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(max_length=4, required=True)
    
    class Meta:
        extra_kwargs = {
            "email": {"validators": []},
            "otp_code": {"validators": []},
        }
      

    def validate_email(self, value):
        """Validate email with global security protection"""
        validated_email = CommonValidators.validate_email_field(
            value, "البريد الإلكتروني"
        )

        # Check if email exists in database
        if not User.objects.filter(email=validated_email , is_deleted=False , is_banned=False).exists():
            raise serializers.ValidationError("البريد الإلكتروني غير مسجل في النظام")

        return validated_email

    def validate_otp_code(self, value):
        """Validate OTP code with global security protection"""
        if not value:
            raise serializers.ValidationError("رمز التحقق مطلوب")

        # Security validation
        try:
            value = SecurityValidator.validate_input(
                value, "رمز التحقق", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        # Check if OTP is 4 digits
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("رمز التحقق يجب أن يكون 4 أرقام")

        return value
    

class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resend OTP request"""

    email = serializers.EmailField(required=True)
    purpose = serializers.ChoiceField(
        choices=[
            ("email_verification", "تأكيد البريد الإلكتروني"),
            ("password_reset", "إعادة تعيين كلمة المرور"),
        ],
        required=True,
    )

    def validate_email(self, value):
        """Validate email with global security protection"""
        validated_email = CommonValidators.validate_email_field(
            value, "البريد الإلكتروني"
        )

        # Check if email exists in database
        if not User.objects.filter(email=validated_email).exists():
            raise serializers.ValidationError("البريد الإلكتروني غير مسجل في النظام")

        return validated_email

    def validate_purpose(self, value):
        """Validate purpose with global security protection"""
        try:
            value = SecurityValidator.validate_input(
                value, "الغرض", check_sql_injection=True, check_xss=False
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        # Validate purpose choices
        valid_purposes = ["email_verification", "password_reset"]
        if value not in valid_purposes:
            raise serializers.ValidationError(
                "الغرض يجب أن يكون إما 'email_verification' أو 'password_reset'"
            )

        return value


class UserResponseSerializer(serializers.ModelSerializer):
    """Serializer for user response data"""

    class Meta:
        model = User
        fields = [
            "uuid",
            "username",
            "email",
            "account_type",
            "is_account_confirmed",
            "balance",
            "created_at",
            "is_banned",
            "banning_reason",
            "banned_date",
            "banned_until",
        ]
        read_only_fields = fields
