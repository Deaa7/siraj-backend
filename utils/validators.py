"""
Global Validators for Django Apps
This module provides common validation utilities for all Django apps
"""

import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .security import SecurityValidator


class CommonValidators:
    """Common validation utilities"""
    
    @staticmethod
    def validate_arabic_text(value, field_name="النص", min_length=2, max_length=150):
        """Validate Arabic text fields"""
        if not value:
            raise ValidationError(f"{field_name} مطلوب")
        
        # Security validation
        value = SecurityValidator.validate_text_field(value, field_name)
        
        # Length validation
        if len(value) < min_length:
            raise ValidationError(f"{field_name} يجب أن يكون على الأقل {min_length} أحرف")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} يجب أن يكون أقل من {max_length} حرف")
        
        # Arabic characters validation
        if not re.match(r"^[\u0600-\u06FF\s\u0750-\u077F\u08A0-\u08FF]+$", value):
            raise ValidationError(f"يجب أن يحتوي {field_name} على أحرف عربية فقط")
        
        return value.strip()
    
    @staticmethod
    def validate_username(value, field_name="اسم المستخدم", min_length=2, max_length=40):
        """Validate username fields"""
        if not value:
            raise ValidationError(f"{field_name} مطلوب")
        
        # Security validation
        value = SecurityValidator.validate_username_field(value, field_name)
        
        # Length validation
        if len(value) < min_length:
            raise ValidationError(f"{field_name} يجب أن يكون على الأقل {min_length} أحرف")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} يجب أن يكون أقل من {max_length} حرف")
        
        # Character validation (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError(f"{field_name} يجب أن يحتوي على أحرف وأرقام وشرطة سفلية فقط")
        
        return value.strip()
    
    @staticmethod
    def validate_team_name(value, field_name="اسم الفريق", min_length=2, max_length=40):
        """Validate username fields"""
        if not value:
            raise ValidationError(f"{field_name} مطلوب")
        
        # Security validation
        value = SecurityValidator.validate_team_name_field(value, field_name)
        
        # Length validation
        if len(value) < min_length:
            raise ValidationError(f"{field_name} يجب أن يكون على الأقل {min_length} أحرف")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} يجب أن يكون أقل من {max_length} حرف")
        
        return value.strip()
    
    @staticmethod
    def validate_email_field(value, field_name="البريد الإلكتروني"):
        """Validate email fields"""
        if not value:
            raise ValidationError(f"{field_name} مطلوب")
        
        # Security validation
        value = SecurityValidator.validate_email_field(value, field_name)
        
        # Email format validation
        try:
            validate_email(value)
        except ValidationError:
            raise ValidationError(f"{field_name} غير صحيح")
        
        return value.lower().strip()
    
    @staticmethod
    def validate_password(value, field_name="كلمة المرور", min_length=6, max_length=128):
        """Validate password fields"""
        if not value:
            raise ValidationError(f"{field_name} مطلوبة")
        
        # Security validation
        value = SecurityValidator.validate_password_field(value, field_name)
        
        # Length validation
        if len(value) < min_length:
            raise ValidationError(f"{field_name} يجب أن تكون على الأقل {min_length} أحرف")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} يجب أن تكون أقل من {max_length} حرف")
        
        # Password strength validation
        if not re.search(r'\d', value):
            raise ValidationError(f"{field_name} يجب أن تحتوي على رقم واحد على الأقل")
        
        if not re.search(r'[a-zA-Z]', value):
            raise ValidationError(f"{field_name} يجب أن تحتوي على حرف واحد على الأقل")
        
        return value
    
    @staticmethod
    def validate_phone(value, field_name="رقم الهاتف", min_length=8, max_length=12):
        """Validate phone number fields"""
        if not value:
            raise ValidationError(f"{field_name} مطلوب")
        
        # Security validation
        value = SecurityValidator.validate_phone_field(value, field_name)
        
        # Remove non-digit characters
        phone_digits = re.sub(r'\D', '', value)
        
        # Length validation
        if len(phone_digits) < min_length or len(phone_digits) > max_length:
            raise ValidationError(f"{field_name} يجب أن يحتوي على {min_length} إلى {max_length} رقم")
        
        return phone_digits
    
 
    @staticmethod
    def validate_url(value, field_name="الرابط"):
        """Validate URL fields"""
        if not value:
            return ""
        
        # Security validation
        value = SecurityValidator.validate_url_field(value, field_name)
        
        # Basic URL validation
        url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        if not re.match(url_pattern, value):
            raise ValidationError(f"{field_name} غير صحيح")
        
        return value.strip()
    
    @staticmethod
    def validate_text_field(value, field_name="النص", max_length=500, allow_empty=False):
        """Validate general text fields"""
        if not value and not allow_empty:
            raise ValidationError(f"{field_name} مطلوب")
        
        if not value and allow_empty:
            return ""
        
        # Security validation
        value = SecurityValidator.validate_text_field(value, field_name)
        
        # Length validation
        if len(value) > max_length:
            raise ValidationError(f"{field_name} يجب أن يكون أقل من {max_length} حرف")
        
        return value.strip()
    
    @staticmethod
    def validate_integer_field(value, field_name="الرقم", min_value=0, max_value=None):
        """Validate integer fields"""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"{field_name} مطلوب")
        
        if isinstance(value, bool):
            raise ValidationError(f"{field_name} يجب أن يكون رقمًا صالحًا")
        
        return int(value)
    
    @staticmethod
    def validate_float_field(value, field_name="الرقم", min_value=0, max_value=None):
        """Validate float fields"""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"{field_name} مطلوب")
        
        if isinstance(value, bool):
            raise ValidationError(f"{field_name} يجب أن يكون رقمًا صالحًا")
        
        return float(value)
    
    @staticmethod
    def validate_money_amount(value, field_name="المبلغ"):
        """Validate money amount fields"""
        if value is None:
            raise ValidationError(f"{field_name} مطلوب")
        
        # Handle empty strings
        if isinstance(value, str) and not value.strip():
            raise ValidationError(f"{field_name} مطلوب")

        # Reject boolean values explicitly (True/False are instances of int)
        if isinstance(value, bool):
            raise ValidationError(f"{field_name} يجب أن يكون رقمًا صالحًا")

        # Handle Decimal type
        if isinstance(value, Decimal):
            value = float(value)
        
        # Convert to string first to normalize the value
        if isinstance(value, (int, float)):
            value = str(value)
        
        if isinstance(value, str):
            numeric_str = value.strip()
            # Accept only numeric strings with optional single decimal point
            # This regex allows: 123, 123.45, 123.0, etc.
            if not re.match(r'^\d+(?:\.\d+)?$', numeric_str):
                raise ValidationError(f"{field_name} يجب أن يكون رقمًا صالحًا بدون أحرف")
            try:
                numeric_value = float(numeric_str)
            except ValueError:
                raise ValidationError(f"{field_name} يجب أن يكون رقمًا صالحًا")
            value = numeric_value
        elif not isinstance(value, (int, float)):
            raise ValidationError(f"{field_name} يجب أن يكون رقمًا صالحًا")
        
        if value < 0:
            raise ValidationError(f"{field_name} يجب أن يكون أكبر من 0")
        
        return float(value)
