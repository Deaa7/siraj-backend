from django.db import models
from django.core.exceptions import ValidationError
from Constants import CITIES
from users.models import User
from django.core.validators import (
    MinValueValidator,
    MinLengthValidator,
    MaxValueValidator,
    URLValidator,
    RegexValidator,
)
from common.models import PublicModel

def validate_social_media_url(value):
    """Validate social media URLs"""
    if value and not any(
        domain in value.lower()
        for domain in [
            "telegram.me",
            "t.me",
            "wa.me",
            "whatsapp.com",
            "instagram.com",
            "facebook.com",
            "twitter.com",
            "x.com",
            "linkedin.com",
        ]
    ):
        raise ValidationError("يجب أن يكون الرابط صحيحاً لوسائل التواصل الاجتماعي")


# Arabic name validator
arabic_validator = RegexValidator(
    regex=r"^[\u0600-\u06FF\s\u0750-\u077F\u08A0-\u08FF]+$",
    message="يجب أن يحتوي الاسم على أحرف عربية فقط",
    code="invalid_arabic",
)

# Phone number validator - choose one from above
phone_validator = RegexValidator(
    regex=r"^[0-9]{8,12}$",
    message="يجب أن يحتوي رقم الهاتف على 8 إلى 12 رقم فقط",
    code="invalid_phone",
)


class TeamProfile(PublicModel):
    # Foreign key to User model
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="team_profile",
        verbose_name="المستخدم",
    )

    # Statistics
    number_of_exams = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0, message="عدد الامتحانات لا يمكن أن يكون سالب")
        ],
        verbose_name="عدد الامتحانات",
        blank=True,
    )

    number_of_notes = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0, message="عدد الملاحظات لا يمكن أن يكون سالب")],
        verbose_name="عدد الملاحظات",
        blank=True,
    )

    number_of_courses = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0, message="عدد الكورسات لا يمكن أن يكون سالب")],
        verbose_name="عدد الكورسات",
        blank=True,
    )

    number_of_followers = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0, message="عدد المتابعين لا يمكن أن يكون سالب")],
        verbose_name="عدد المتابعين",
        blank=True,
    )

    # Social Media Links
    telegram_link = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        validators=[validate_social_media_url],
        verbose_name="رابط التليجرام",
    )

    whatsapp_link = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        validators=[validate_social_media_url],
        verbose_name="رابط الواتساب",
    )

    instagram_link = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        validators=[validate_social_media_url],
        verbose_name="رابط الانستغرام",
    )

    facebook_link = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        validators=[validate_social_media_url],
        verbose_name="رابط الفيسبوك",
    )

    x_link = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        validators=[validate_social_media_url],
        verbose_name="رابط إكس (تويتر)",
    )

    linkedin_link = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        validators=[validate_social_media_url],
        verbose_name="رابط لينكد إن",
    )

    # Profile Status
    verified = models.BooleanField(default=False, verbose_name="حساب موثق")

    address = models.TextField(
        max_length=500, verbose_name="العنوان", help_text="العنوان الكامل", blank=True
    )

    bio = models.TextField(
        max_length=1000,
        blank=True,
        verbose_name="نبذة شخصية",
        help_text="اكتب نبذة عن الفريق وخبراته",
    )

    years_of_experience = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0, message="سنوات الخبرة لا يمكن أن تكون سالبة"),
            MaxValueValidator(
                50, message="سنوات الخبرة لا يمكن أن تكون أكثر من 50 سنة"
            ),
        ],
        verbose_name="سنوات الخبرة",
    )

    class Meta:
        verbose_name = "ملف الفريق"
        verbose_name_plural = "ملفات الفرق"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['-number_of_exams']),
            models.Index(fields=['-number_of_notes']),
            models.Index(fields=['-number_of_courses']),
            models.Index(fields=['-number_of_followers']),
        ]

    def __str__(self):
        return f"ملف الفريق: {self.user.team_name}"
