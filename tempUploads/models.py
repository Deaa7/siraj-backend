from django.db import models
from common.models import PublicModel
# Create your models here.

class TempUpload(PublicModel):
    name = models.CharField(max_length=500, verbose_name="اسم الملف")
    expiration_date = models.DateTimeField(verbose_name="تاريخ الانتهاء" , blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["expiration_date"]),
            models.Index(fields=["name"]),
        ]