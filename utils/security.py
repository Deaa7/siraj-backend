"""
Global Security Utilities for SQL Injection Detection and Prevention
This module provides comprehensive SQL injection protection for all Django apps
"""

import re
import html
from django.core.exceptions import ValidationError


class SQLInjectionDetector:
    """Comprehensive SQL injection detection and prevention"""
    
    # Common SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        # Basic SQL injection patterns
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
        r"(\bUNION\s+SELECT\b)",
        r"(\bDROP\s+TABLE\b)",
        r"(\bDELETE\s+FROM\b)",
        r"(\bINSERT\s+INTO\b)",
        r"(\bUPDATE\s+SET\b)",
        r"(\bALTER\s+TABLE\b)",
        r"(\bCREATE\s+TABLE\b)",
        r"(\bEXEC\s*\()",
        r"(\bEXECUTE\s*\()",
        r"(\bSCRIPT\b)",
        
        # Comment patterns
        r"(--|\#|\/\*|\*\/)",
        
        # Quote manipulation
        r"(['\"]\s*;\s*--)",
        r"(['\"]\s*;\s*DROP)",
        r"(['\"]\s*;\s*DELETE)",
        r"(['\"]\s*;\s*INSERT)",
        r"(['\"]\s*;\s*UPDATE)",
        
        # Time-based blind SQL injection
        r"(\bSLEEP\s*\()",
        r"(\bWAITFOR\s+DELAY\b)",
        r"(\bBENCHMARK\s*\()",
        
        # Boolean-based blind SQL injection
        r"(\bAND\s+\d+\s*=\s*\d+)",
        r"(\bOR\s+\d+\s*=\s*\d+)",
        r"(\bAND\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
        r"(\bOR\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
        
        # Error-based SQL injection
        r"(\bEXTRACTVALUE\s*\()",
        r"(\bUPDATEXML\s*\()",
        r"(\bCONCAT\s*\()",
        
        # Stacked queries
        r"(\b;\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER))",
        
        # System functions
        r"(\bUSER\s*\(\s*\))",
        r"(\bDATABASE\s*\(\s*\))",
        r"(\bVERSION\s*\(\s*\))",
        r"(\b@@VERSION)",
        r"(\b@@DATABASE)",
        r"(\b@@USER)",
        
        # Information schema
        r"(\bINFORMATION_SCHEMA\b)",
        r"(\bSYSOBJECTS\b)",
        r"(\bSYSCOLUMNS\b)",
        
        # Dangerous functions
        r"(\bLOAD_FILE\s*\()",
        r"(\bINTO\s+OUTFILE\b)",
        r"(\bINTO\s+DUMPFILE\b)",
        
        # Hex encoding attempts
        r"(0x[0-9a-fA-F]+)",
        
        # Base64 encoding attempts
        # r"([A-Za-z0-9+/]{4,}={0,2})",
        
        # # URL encoding attempts
        # r"(%[0-9a-fA-F]{2})",
        
        # Special characters that can be used for SQL injection
        r"([;'\"\\])",
        r"(\bNULL\b)",
        r"(\bTRUE\b)",
        r"(\bFALSE\b)",
    ]
    
    # Additional dangerous patterns for specific contexts
    DANGEROUS_PATTERNS = [
        r"(\bxp_cmdshell\b)",
        r"(\bsp_executesql\b)",
        r"(\bOPENROWSET\b)",
        r"(\bOPENDATASOURCE\b)",
        r"(\bBULK\s+INSERT\b)",
        r"(\bBCP\b)",
        r"(\bREGEXP\b)",
        r"(\bRLIKE\b)",
        r"(\bMATCH\s+AGAINST\b)",
    ]
    
    @classmethod
    def detect_sql_injection(cls, value):
        """
        Detect SQL injection attempts in input value
        Returns True if SQL injection is detected, False otherwise
        """
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        
        # Check for suspicious character combinations
        suspicious_combinations = [
            r"'\s*or\s*'",
            r"\"\s*or\s*\"",
            r"'\s*and\s*'",
            r"\"\s*and\s*\"",
            r"'\s*union\s*'",
            r"\"\s*union\s*\"",
            r"'\s*select\s*'",
            r"\"\s*select\s*\"",
            r"'\s*insert\s*'",
            r"\"\s*insert\s*\"",
            r"'\s*update\s*'",
            r"\"\s*update\s*\"",
            r"'\s*delete\s*'",
            r"\"\s*delete\s*\"",
            r"'\s*drop\s*'",
            r"\"\s*drop\s*\"",
        ]
        
        for pattern in suspicious_combinations:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def sanitize_input(cls, value):
        """
        Sanitize input to prevent SQL injection
        """
        if not isinstance(value, str):
            return value
        
        # HTML escape to prevent XSS
        sanitized = html.escape(value)
        
        # Remove or replace dangerous characters
        dangerous_chars = [';', "'", '"', '\\', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    @classmethod
    def validate_and_sanitize(cls, value, field_name="field"):
        """
        Validate input for SQL injection and sanitize if safe
        """
        if cls.detect_sql_injection(value):
           
            raise ValidationError(f"تم اكتشاف محاولة حقن SQL في حقل {field_name}. يرجى إدخال بيانات صحيحة.")
        
        return cls.sanitize_input(value)


class XSSDetector:
    """XSS (Cross-Site Scripting) detection and prevention"""
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<applet[^>]*>.*?</applet>",
        r"<meta[^>]*>.*?</meta>",
        r"<link[^>]*>.*?</link>",
        r"<style[^>]*>.*?</style>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onfocus\s*=",
        r"onblur\s*=",
        r"onchange\s*=",
        r"onsubmit\s*=",
        r"onreset\s*=",
        r"onselect\s*=",
        r"onunload\s*=",
    ]
    
    @classmethod
    def detect_xss(cls, value):
        """Detect XSS attempts in input value"""
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def sanitize_input(cls, value):
        """Sanitize input to prevent XSS"""
        if not isinstance(value, str):
            return value
        
        # HTML escape
        sanitized = html.escape(value)
        
        return sanitized.strip()
    
    @classmethod
    def validate_and_sanitize(cls, value, field_name="field"):
        """Validate input for XSS and sanitize if safe"""
        if cls.detect_xss(value):
            raise ValidationError(f"تم اكتشاف محاولة XSS في حقل {field_name}. يرجى إدخال بيانات صحيحة.")
        
        return cls.sanitize_input(value)


class SecurityValidator:
    """Combined security validator for SQL injection and XSS"""
    
    @classmethod
    def validate_input(cls, value, field_name="field", check_sql_injection=True, check_xss=True):
        """
        Comprehensive security validation for input
        """
        if not isinstance(value, str):
            return value
        
        # Check SQL injection
        if check_sql_injection and SQLInjectionDetector.detect_sql_injection(value):
            raise ValidationError(f"تم اكتشاف محاولة حقن SQL في حقل {field_name}. يرجى إدخال بيانات صحيحة.")
        
        # Check XSS
        if check_xss and XSSDetector.detect_xss(value):
            raise ValidationError(f"تم اكتشاف محاولة XSS في حقل {field_name}. يرجى إدخال بيانات صحيحة.")
        
        # Sanitize input
        sanitized = html.escape(value)
        
        # Remove dangerous characters
        dangerous_chars = [';', "'", '"', '\\', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    @classmethod
    def validate_text_field(cls, value, field_name="field"):
        """Validate text fields (names, descriptions, etc.)"""
        return cls.validate_input(value, field_name, check_sql_injection=True, check_xss=True)
    
    @classmethod
    def validate_username_field(cls, value, field_name="اسم المستخدم"):
        """Validate username fields"""
        return cls.validate_input(value, field_name, check_sql_injection=True, check_xss=True)
    
    @classmethod
    def validate_team_name_field(cls, value, field_name="اسم الفريق"):
        """Validate team name fields"""
        return cls.validate_input(value, field_name, check_sql_injection=True, check_xss=True)
        
    @classmethod
    def validate_email_field(cls, value, field_name="البريد الإلكتروني"):
        """Validate email fields"""
        return cls.validate_input(value, field_name, check_sql_injection=True, check_xss=False)
    
    @classmethod
    def validate_password_field(cls, value, field_name="كلمة المرور"):
        """Validate password fields"""
        return cls.validate_input(value, field_name, check_sql_injection=True, check_xss=False)
    
    @classmethod
    def validate_phone_field(cls, value, field_name="رقم الهاتف"):
        """Validate phone fields"""
        return cls.validate_input(value, field_name, check_sql_injection=True, check_xss=False)
    
    @classmethod
    def validate_url_field(cls, value, field_name="الرابط"):
        """Validate URL fields"""
        return cls.validate_input(value, field_name, check_sql_injection=True, check_xss=True)
