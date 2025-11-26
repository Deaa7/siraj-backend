from django.contrib import admin

# Register your models here.
from .models import MCQ
@admin.register(MCQ)
class MCQAdmin(admin.ModelAdmin):
    list_display = ["id", "exam", "question", "question_image", "option_A", "option_B", "option_C", "option_D", "option_E", "right_answer", "explanation", "is_arabic"]
    