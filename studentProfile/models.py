from django.db import models
from django.core.validators import MinValueValidator, RegexValidator , MinLengthValidator
from Constants import CITIES, CLASSES, GENDERS
from users.models import User
from common.models import PublicModel

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
 
class StudentProfile(PublicModel):
    # Foreign key to User model
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile',
        verbose_name="المستخدم"
    )
 
  
 
    Class = models.CharField(
        max_length=6,
        choices=CLASSES,
        verbose_name="الصف",
        help_text="الصف الذي تدرس فيه"
    )
    
    school = models.CharField(
        max_length=100,
        verbose_name="المدرسة",
        help_text="اسم المدرسة التي تدرس فيها",
        validators=[
            MinLengthValidator(2, "يجب ألا يكون الاسم الأول أقصر من حرفين"),
            arabic_validator,
        ],
        blank=True,
    )
    
    # Statistics
    number_of_done_exams = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0, message="عدد الامتحانات المنجزة لا يمكن أن يكون سالب")],
        verbose_name="عدد الامتحانات المنجزة",
        blank=True,
    )
    
    number_of_read_notes = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0, message="عدد الملاحظات المقروءة لا يمكن أن يكون سالب")],
        verbose_name="عدد الملاحظات المقروءة",
        blank=True,
    )
    
    number_of_completed_courses = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0, message="عدد الكورسات المكتملة لا يمكن أن يكون سالب")],
        verbose_name="عدد الكورسات المكتملة",
        blank=True,
    )
    
    class Meta:
        verbose_name = "ملف الطالب"
        verbose_name_plural = "ملفات الطلاب"
        ordering = ['-id']
    
    def __str__(self):
        return f"ملف الطالب: {self.user.first_name} {self.user.last_name}"
