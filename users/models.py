from enum import unique
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MinLengthValidator, RegexValidator
from Constants import CITIES, GENDERS
import uuid

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


class User(AbstractUser):

    ACCOUNT_TYPES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("team", "Team"),
        ("admin", "Admin"),
    ]

    email = models.EmailField(unique=True )

    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPES, default="student"
    )

    first_name = models.CharField(
        max_length=150,
        validators=[
            MinLengthValidator(2, "يجب ألا يكون الاسم الأول أقصر من حرفين"),
            arabic_validator,
        ],
    )

    last_name = models.CharField(
        max_length=150,
        validators=[
            arabic_validator,
        ],
        default="",
        blank=True,
    )

    full_name = models.CharField(
        max_length=250,
        default="",
        verbose_name="الاسم الكامل",
        help_text="اسم المعلم الكامل",
        blank=True,
    )

    team_name = models.CharField(
        max_length=250,
        default="",
        verbose_name="اسم الفريق",
        help_text="اسم الفريق",
        blank=True,
    )

    # Basic Information
    phone = models.CharField(
        max_length=12,
        validators=[
            MinLengthValidator(7, "يجب ألا يكون الاسم الأخير أقصر من 7 حروف"),
            phone_validator,
        ],
        unique=True,
    )

    image = models.CharField(max_length=300, blank=True)

    gender = models.CharField(
        max_length=2,
        default="M",
        choices=GENDERS,
        blank=True,
    )

    city = models.CharField(max_length=60, default="حمص", choices=CITIES)

    is_account_confirmed = models.BooleanField(default=False, blank=True)

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )

    balance = models.IntegerField(
        default=0,
        blank=True,
        validators=[MinValueValidator(0, message="لا يمكن للرصيد أن يكون سالب")],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    is_banned = models.BooleanField(default=False, blank=True)

    banned_date = models.DateField(blank=True, null=True)

    banning_reason = models.CharField(max_length=2000, blank=True)

    banned_until = models.DateField(
        blank=True, null=True
    )  # make it null if we want to ban the user forever

    is_deleted = models.BooleanField(default=False, blank=True)

    deleted_reason = models.CharField(max_length=2000, blank=True)

    # telegram_chat_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]  # Newest users first by default
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]

    def save(self, *args, **kwargs):
        # Set full_name from first_name and last_name
        if self.first_name and self.last_name and self.account_type != "team":
            self.full_name = f"{self.first_name} {self.last_name}".strip()
        elif self.account_type == "team":
            self.full_name = self.team_name.strip()
        elif self.first_name:
            self.full_name = self.first_name.strip()
        else:
            self.full_name = ""
        super().save(*args, **kwargs)
