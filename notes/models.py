from django.core.validators import MinLengthValidator
from django.db import models

# Create your models here.
from Constants import CLASSES, LEVELS, SUBJECT_NAMES
from users.models import User
from django.core.validators import MinValueValidator

from common.models import PublicModel


class Note(PublicModel):
    name = models.CharField(max_length=300, validators=[MinLengthValidator(2)])
    
    subject_name = models.CharField(
        max_length=60, choices=SUBJECT_NAMES, default="math"
    )
    Class = models.CharField(max_length=6, choices=CLASSES, default="12")
    
    publisher_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    
    content = models.CharField(max_length=300, validators=[MinLengthValidator(2)])
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    
    number_of_downloads = models.IntegerField(
        default=0, blank=True, validators=[MinValueValidator(0)]
    )
    
    number_of_purchases = models.IntegerField(
        default=0, blank=True, validators=[MinValueValidator(0)]
    )
    
    number_of_comments = models.IntegerField(
        default=0, blank=True, validators=[MinValueValidator(0)]
    )
   
    number_of_pages = models.IntegerField(
        default=0, blank=True, validators=[MinValueValidator(0)]
    )
    
    file_size = models.IntegerField(
        default=0, blank=True, validators=[MinValueValidator(0)]
    )
    
    active = models.BooleanField(default=True, blank=True)
    
    disable_date = models.DateTimeField(null=True, blank=True)
    
    disabled_by = models.CharField(max_length=50, default="", blank=True, null=True)
    
    level = models.CharField(max_length=6, default="سهل", choices=LEVELS, blank=True)
    
    description = models.TextField(
        max_length=1500, default="", validators=[MinLengthValidator(2)],
        blank = True        
    )
    
    visibility = models.CharField(max_length=10, default="public", blank=True)
    
    profit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        indexes = [
            models.Index(fields=[ 'active' , 'visibility' ,'subject_name','Class', '-created_at']),
            models.Index(fields=[ 'active' , 'visibility' ,'subject_name','Class', '-number_of_downloads' ]),
            models.Index(fields=[ 'active' , 'visibility' ,'subject_name','Class', '-number_of_purchases' ]),
            # models.Index(fields=[ 'active' , 'visibility' ,'subject_name','Class', '-number_of_reads' ]),
        ]

     
