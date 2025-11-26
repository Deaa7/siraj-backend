from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string
from common.models import PublicModel

class UserOTP(PublicModel):
    # Foreign key to User model
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='otps',
        verbose_name="المستخدم"
    )
    
    # OTP code (4-digit number)
    otp_code = models.CharField(
        max_length=4,
        verbose_name="رمز التحقق",
        help_text="رمز التحقق المكون من 4 أرقام"
    )
    
    # Timestamp when OTP expires (default: 15 minutes from creation)
    expire_at = models.DateTimeField(
        verbose_name="تاريخ الانتهاء"
    )
    
    # Whether OTP has been used
    is_used = models.BooleanField(
        default=False,
        verbose_name="تم الاستخدام",
        blank=True,
    )
    
    # Purpose of OTP (email verification, password reset, etc.)
    purpose = models.CharField(
        max_length=50,
        default="email_verification",
        verbose_name="الغرض",
        help_text="الغرض من رمز التحقق"
    )
    
    class Meta:
        verbose_name = "رمز تحقق المستخدم"
        verbose_name_plural = "رموز تحقق المستخدمين"
    
    def __str__(self):
        return f"رمز التحقق للمستخدم: {self.user.username} - {self.otp_code}"
    
    def save(self, *args, **kwargs):
        # Generate OTP code if not provided
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        
        # Set expiration time if not provided (15 minutes from now)
        if not self.expire_at:
            self.expire_at = timezone.now() + timedelta(minutes=15)
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_otp():
        """Generate a 4-digit OTP code"""
        return ''.join(random.choices(string.digits, k=4))
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expire_at
    
    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.save()
