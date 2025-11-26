# Global Security Utilities for Django Apps

This package provides comprehensive security utilities for all Django apps in the project.

## Structure

```
utils/
├── __init__.py
├── security.py      # SQL injection and XSS detection
├── validators.py    # Common validation utilities
└── helpers.py       # General helper functions
```

## Usage

### 1. Security Protection

#### SQL Injection Detection
```python
from utils.security import SQLInjectionDetector

# Detect SQL injection
if SQLInjectionDetector.detect_sql_injection(user_input):
    print("SQL injection detected!")

# Sanitize input
clean_input = SQLInjectionDetector.sanitize_input(user_input)

# Validate and sanitize
try:
    clean_input = SQLInjectionDetector.validate_and_sanitize(user_input, "field_name")
except ValidationError as e:
    print(str(e))
```

#### XSS Detection
```python
from utils.security import XSSDetector

# Detect XSS
if XSSDetector.detect_xss(user_input):
    print("XSS detected!")

# Sanitize input
clean_input = XSSDetector.sanitize_input(user_input)

# Validate and sanitize
try:
    clean_input = XSSDetector.validate_and_sanitize(user_input, "field_name")
except ValidationError as e:
    print(str(e))
```

#### Combined Security Validator
```python
from utils.security import SecurityValidator

# Comprehensive validation
clean_input = SecurityValidator.validate_input(
    user_input, 
    "field_name", 
    check_sql_injection=True, 
    check_xss=True
)

# Field-specific validation
username = SecurityValidator.validate_username_field(username, "اسم المستخدم")
email = SecurityValidator.validate_email_field(email, "البريد الإلكتروني")
password = SecurityValidator.validate_password_field(password, "كلمة المرور")
phone = SecurityValidator.validate_phone_field(phone, "رقم الهاتف")
url = SecurityValidator.validate_url_field(url, "الرابط")
```

### 2. Common Validators

```python
from utils.validators import CommonValidators

# Arabic text validation
name = CommonValidators.validate_arabic_text(name, "الاسم", min_length=2, max_length=150)

# Username validation
username = CommonValidators.validate_username(username, "اسم المستخدم", min_length=2, max_length=40)

# Email validation
email = CommonValidators.validate_email_field(email, "البريد الإلكتروني")

# Password validation
password = CommonValidators.validate_password(password, "كلمة المرور", min_length=6, max_length=128)

# Phone validation
phone = CommonValidators.validate_phone(phone, "رقم الهاتف", min_length=8, max_length=12)

# Gender validation
gender = CommonValidators.validate_gender(gender, "الجنس")

# URL validation
url = CommonValidators.validate_url(url, "الرابط")

# General text validation
text = CommonValidators.validate_text_field(text, "النص", max_length=500, allow_empty=False)
```

### 3. Helper Functions

```python
from utils.helpers import StringHelpers, DateTimeHelpers, ValidationHelpers, FileHelpers, ResponseHelpers

# String helpers
unique_id = StringHelpers.generate_unique_id(8)
hash_value = StringHelpers.generate_hash("password")
clean_phone = StringHelpers.clean_phone_number("+963 11 234 5678")
formatted_phone = StringHelpers.format_phone_number("0112345678")
truncated = StringHelpers.truncate_text("Long text...", 50)

# DateTime helpers
current_time = DateTimeHelpers.get_current_time()
future_time = DateTimeHelpers.add_days_to_now(7)
is_expired = DateTimeHelpers.is_expired(some_time)
formatted_time = DateTimeHelpers.format_datetime(current_time)

# Validation helpers
is_valid_email = ValidationHelpers.is_valid_email("user@example.com")
is_valid_phone = ValidationHelpers.is_valid_phone("0112345678")
is_valid_url = ValidationHelpers.is_valid_url("https://example.com")
is_strong_password = ValidationHelpers.is_strong_password("MyPass123!")

# File helpers
extension = FileHelpers.get_file_extension("image.jpg")
is_image = FileHelpers.is_image_file("photo.png")
is_document = FileHelpers.is_document_file("document.pdf")
new_filename = FileHelpers.generate_filename("old_file.jpg", "new_")

# Response helpers
success_response = ResponseHelpers.success_response("تم بنجاح", data)
error_response = ResponseHelpers.error_response("حدث خطأ", errors)
validation_error = ResponseHelpers.validation_error_response(errors)
not_found = ResponseHelpers.not_found_response()
unauthorized = ResponseHelpers.unauthorized_response()
forbidden = ResponseHelpers.forbidden_response()
server_error = ResponseHelpers.server_error_response()
```

## Integration with Serializers

### Before (Local Implementation)
```python
class UserSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError("اسم المستخدم مطلوب")
        
        # SQL injection detection
        try:
            value = SQLInjectionDetector.validate_and_sanitize(value, "اسم المستخدم")
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        # Length validation
        if len(value) < 2:
            raise serializers.ValidationError("اسم المستخدم يجب أن يكون على الأقل 2 أحرف")
        
        # Character validation
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("اسم المستخدم يجب أن يحتوي على أحرف وأرقام وشرطة سفلية فقط")
        
        return value
```

### After (Global Implementation)
```python
class UserSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        return CommonValidators.validate_username(value, "اسم المستخدم")
```

## Benefits

1. **Consistency**: Same validation logic across all apps
2. **Maintainability**: Update security patterns in one place
3. **Reusability**: Use the same validators everywhere
4. **Security**: Comprehensive protection against SQL injection and XSS
5. **Performance**: Optimized regex patterns and validation logic
6. **Extensibility**: Easy to add new validation patterns

## Security Features

### SQL Injection Protection
- Basic SQL injection patterns
- Time-based blind SQL injection
- Boolean-based blind SQL injection
- Error-based SQL injection
- Stacked queries
- System functions
- Information schema
- Dangerous functions
- Encoding attempts
- Suspicious character combinations

### XSS Protection
- Script tags
- Iframe tags
- Object tags
- Event handlers
- JavaScript protocols
- VBScript protocols
- HTML entities

### Input Sanitization
- HTML escaping
- Dangerous character removal
- Input trimming
- Character encoding protection

## Examples

### Detecting SQL Injection Attempts
```python
# These inputs will be detected and blocked:
malicious_inputs = [
    "admin' OR '1'='1",
    "'; DROP TABLE users; --",
    "admin' UNION SELECT * FROM users --",
    "admin' AND SLEEP(5) --",
    "admin' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()), 0x7e)) --",
    "admin' AND 1=1 --",
    "admin' OR 1=1 --",
]

for input_val in malicious_inputs:
    if SQLInjectionDetector.detect_sql_injection(input_val):
        print(f"Blocked: {input_val}")
```

### Detecting XSS Attempts
```python
# These inputs will be detected and blocked:
xss_inputs = [
    "<script>alert('XSS')</script>",
    "<iframe src='javascript:alert(1)'></iframe>",
    "javascript:alert('XSS')",
    "onclick=alert('XSS')",
    "<img src=x onerror=alert('XSS')>",
]

for input_val in xss_inputs:
    if XSSDetector.detect_xss(input_val):
        print(f"Blocked: {input_val}")
```

## Best Practices

1. **Always use global validators** instead of implementing local ones
2. **Import specific classes** you need to avoid circular imports
3. **Use field-specific validators** for better error messages
4. **Test your validators** with malicious inputs
5. **Keep validators updated** with new security patterns
6. **Use helper functions** for common operations
7. **Format responses consistently** using ResponseHelpers

## Migration Guide

To migrate existing serializers to use global utilities:

1. **Add imports**:
   ```python
   from utils.security import SecurityValidator
   from utils.validators import CommonValidators
   ```

2. **Replace local validators**:
   ```python
   # Old
   def validate_username(self, value):
       # Long validation logic...
   
   # New
   def validate_username(self, value):
       return CommonValidators.validate_username(value, "اسم المستخدم")
   ```

3. **Remove local security classes** (if any)

4. **Test thoroughly** to ensure same behavior

## Support

For questions or issues with the global utilities, please check:
1. This documentation
2. The source code in `utils/` directory
3. Existing implementations in `users/serializers.py`
