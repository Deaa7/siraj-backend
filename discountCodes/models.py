from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models

# Create your models here.
from users.models import User
from exams.models import Exam
from notes.models import Note
from courses.models import Course
from publisherOffers.models import PublisherOffers
from common.models import PublicModel


class DiscountCodes(PublicModel):
    options =[
        ("exam", "امتحان"),
        ("note", "نوطة"),
        ("course", "دورة"),
        ("offer", "عرض"),
    ]
    discount_types =[
        ("percentage", "percentage"),
        ("fixed", "fixed"),
    ]
    
    publisher_id = models.ForeignKey(User, on_delete=models.CASCADE)
    discount_for = models.CharField(max_length= 50, default='امتحان', choices=options)
    exam_id = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True)
    note_id = models.ForeignKey(Note, on_delete=models.CASCADE, null=True, blank=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    offer_id = models.ForeignKey(PublisherOffers, on_delete=models.CASCADE, null=True, blank=True)
   
    discount_type = models.CharField(max_length= 20, default='fixed', choices=discount_types)#percentage, fixed
    discount_value = models.DecimalField(max_digits=10, decimal_places=2,default=0 , validators=[MinValueValidator(0)])
    discount_code = models.CharField(max_length= 25, validators=[MinLengthValidator(2)] )
    valid_until = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True, blank=True)
    number_of_uses = models.IntegerField(default=0, blank=True, validators=[MinValueValidator(0)])
    number_of_remaining_uses = models.IntegerField(blank=True , null=True, default=1000000,  validators=[MinValueValidator(0)])

    class Meta:
        indexes = [
            models.Index(fields=[ '-created_at']),
        ]
    
    
 