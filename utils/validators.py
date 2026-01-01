import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .security import SecurityValidator

class CommonValidators:
    """Optimized validation utilities supporting HTML and LaTeX"""
    
    @staticmethod
    def validate_arabic_text(value, field_name="النص", min_length=2, max_length=5000):
        """Allows Arabic text, HTML, and LaTeX formulas"""
        if not value:
            raise ValidationError(f"{field_name} مطلوب")
        
        # Pass to security validator (which should use bleach.clean to allow safe tags)
        value = SecurityValidator.validate_text_field(value, field_name)
        
        # Length validation
        if not (min_length <= len(value) <= max_length):
            raise ValidationError(f"{field_name} يجب أن يكون بين {min_length} و {max_length} حرف")
        
        # Simplified regex: We allow Arabic range AND basic symbols used in HTML/LaTeX
        # This allows \ { } [ ] < > / and standard Arabic chars
        math_html_arabic_pattern = r"^[\u0600-\u06FF\s0-9a-zA-Z\\{}<>\[\]/_.,!?;:()='\"&-]+$"
        
        # If you want to be even more dynamic, you can skip regex for complex HTML fields
        # and rely purely on the SecurityValidator/Bleach cleaning.
        if not re.match(math_html_arabic_pattern, value, re.DOTALL):
             raise ValidationError(f"يجب أن يحتوي {field_name} على تنسيق صحيح")
        
        return value.strip()

    @staticmethod
    def validate_text_field(value, field_name="النص", max_length=5000, allow_empty=False):
        """General text field supporting HTML/LaTeX"""
        if value is None or (isinstance(value, str) and not value.strip()):
         if allow_empty:
            return ""
         else:
            raise ValidationError(f"{field_name} مطلوب")
        
        # Security cleaning
        value = SecurityValidator.validate_text_field(value, field_name)
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} طويل جداً (الحد الأقصى {max_length})")
        
        return value.strip()

    @staticmethod
    def validate_username(value, field_name="اسم المستخدم", min_length=2, max_length=40):
        if not value: raise ValidationError(f"{field_name} مطلوب")
        value = SecurityValidator.validate_username_field(value, field_name)
        
        if not (min_length <= len(value) <= max_length):
            raise ValidationError(f"{field_name} طول غير مسموح به")
            
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError(f"{field_name} أحرف وأرقام وشرطة سفلية فقط")
        return value.strip()

    @staticmethod
    def validate_email_field(value, field_name="البريد الإلكتروني"):
        if not value: raise ValidationError(f"{field_name} مطلوب")
        value = SecurityValidator.validate_email_field(value, field_name)
        try:
            validate_email(value)
        except ValidationError:
            raise ValidationError(f"{field_name} غير صحيح")
        return value.lower().strip()

    @staticmethod
    def validate_password(value, field_name="كلمة المرور", min_length=6):
        if not value: raise ValidationError(f"{field_name} مطلوبة")
        if len(value) < min_length:
            raise ValidationError(f"{field_name} قصيرة جداً")
        if not re.search(r'\d', value) or not re.search(r'[a-zA-Z]', value):
            raise ValidationError(f"{field_name} يجب أن تحتوي حرف ورقم")
        return value

    @staticmethod
    def validate_phone(value, field_name="رقم الهاتف"):
        if not value: raise ValidationError(f"{field_name} مطلوب")
        digits = re.sub(r'\D', '', str(value))
        if not (8 <= len(digits) <= 15):
            raise ValidationError(f"{field_name} غير صالح")
        return digits

    @staticmethod
    def validate_money_amount(value, field_name="المبلغ"):
        if value is None or isinstance(value, bool):
            raise ValidationError(f"{field_name} مطلوب")
        try:
            amount = float(value)
            if amount < 0: raise ValueError
            return amount
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} رقم غير صالح")