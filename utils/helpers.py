"""
Global Helper Functions for Django Apps
This module provides common helper functions for all Django apps
"""

import re
import uuid
import hashlib
from datetime import  timedelta
from django.utils import timezone



class StringHelpers:
    """String manipulation utilities"""
    
    @staticmethod
    def generate_unique_id(length=8):
        """Generate a unique ID"""
        return str(uuid.uuid4())[:length]
    
    @staticmethod
    def generate_hash(value, algorithm='sha256'):
        """Generate hash for a value"""
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(value.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def clean_phone_number(phone):
        """Clean phone number (remove non-digits)"""
        return re.sub(r'\D', '', phone)
    
    @staticmethod
    def format_phone_number(phone, country_code='+963'):
        """Format phone number with country code"""
        cleaned = StringHelpers.clean_phone_number(phone)
        if cleaned.startswith('0'):
            cleaned = cleaned[1:]
        return f"{country_code}{cleaned}"
    
    @staticmethod
    def truncate_text(text, max_length=100, suffix='...'):
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-len(suffix)] + suffix


class DateTimeHelpers:
    """Date and time utilities"""
    
    @staticmethod
    def get_current_time():
        """Get current timezone-aware datetime"""
        return timezone.now()
    
    @staticmethod
    def add_days_to_now(days):
        """Add days to current time"""
        return timezone.now() + timedelta(days=days)
    
    @staticmethod
    def add_hours_to_now(hours):
        """Add hours to current time"""
        return timezone.now() + timedelta(hours=hours)
    
    @staticmethod
    def add_minutes_to_now(minutes):
        """Add minutes to current time"""
        return timezone.now() + timedelta(minutes=minutes)
    
    @staticmethod
    def is_expired(expiry_time):
        """Check if a time has expired"""
        return timezone.now() > expiry_time
    
    @staticmethod
    def format_datetime(dt, format_string='%Y-%m-%d %H:%M:%S'):
        """Format datetime to string"""
        return dt.strftime(format_string)


class ValidationHelpers:
    """Validation helper functions"""
    
    @staticmethod
    def is_valid_email(email):
        """Check if email is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_phone(phone):
        """Check if phone number is valid"""
        cleaned = StringHelpers.clean_phone_number(phone)
        return len(cleaned) >= 8 and len(cleaned) <= 12
    
    @staticmethod
    def is_valid_url(url):
        """Check if URL is valid"""
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def is_strong_password(password):
        """Check if password is strong"""
        if len(password) < 8:
            return False
        
        has_digit = bool(re.search(r'\d', password))
        has_letter = bool(re.search(r'[a-zA-Z]', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        return has_digit and has_letter and has_special


class FileHelpers:
    """File handling utilities"""
    
    @staticmethod
    def get_file_extension(filename):
        """Get file extension"""
        return filename.split('.')[-1].lower() if '.' in filename else ''
    
    @staticmethod
    def is_image_file(filename):
        """Check if file is an image"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        return FileHelpers.get_file_extension(filename) in image_extensions
    
    @staticmethod
    def is_document_file(filename):
        """Check if file is a document"""
        doc_extensions = ['pdf', 'doc', 'docx', 'txt', 'rtf']
        return FileHelpers.get_file_extension(filename) in doc_extensions
    
    @staticmethod
    def generate_filename(original_filename, prefix=''):
        """Generate unique filename"""
        extension = FileHelpers.get_file_extension(original_filename)
        unique_id = StringHelpers.generate_unique_id()
        return f"{prefix}{unique_id}.{extension}" if extension else f"{prefix}{unique_id}"


class ResponseHelpers:
    """Response formatting utilities"""
    
    @staticmethod
    def success_response(message, data=None, status_code=200):
        """Format success response"""
        response = {
            'success': True,
            'message': message,
            'status_code': status_code
        }
        if data is not None:
            response['data'] = data
        return response
    
    @staticmethod
    def error_response(message, errors=None, status_code=400):
        """Format error response"""
        response = {
            'success': False,
            'message': message,
            'status_code': status_code
        }
        if errors is not None:
            response['errors'] = errors
        return response
    
    @staticmethod
    def validation_error_response(errors, message="خطأ في التحقق من البيانات"):
        """Format validation error response"""
        return ResponseHelpers.error_response(message, errors, 400)
    
    @staticmethod
    def not_found_response(message="العنصر غير موجود"):
        """Format not found response"""
        return ResponseHelpers.error_response(message, status_code=404)
    
    @staticmethod
    def unauthorized_response(message="غير مصرح لك بالوصول"):
        """Format unauthorized response"""
        return ResponseHelpers.error_response(message, status_code=401)
    
    @staticmethod
    def forbidden_response(message="ممنوع الوصول"):
        """Format forbidden response"""
        return ResponseHelpers.error_response(message, status_code=403)
    
    @staticmethod
    def server_error_response(message="خطأ في الخادم"):
        """Format server error response"""
        return ResponseHelpers.error_response(message, status_code=500)
