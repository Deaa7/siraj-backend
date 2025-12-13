# units/models.py
from django.db import models
from django.utils.text import slugify
from Constants import CLASSES_DICT , SUBJECT_NAMES
from common.models import PublicModel

class Unit(PublicModel):
    """
    Shared Unit model that can be used by multiple resource apps.
    Unit names are unique across the entire system.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Unique name for this unit/tag (e.g., 'Algebra Basics', 'Organic Chemistry')"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of what this unit covers",
        max_length=500,
    )
    Class = models.CharField( choices=CLASSES_DICT, max_length=200)
    subject_name = models.CharField( choices=SUBJECT_NAMES, max_length=200)
    slug = models.SlugField(
        max_length=250,
        unique=True,
        editable=False,
        help_text="URL-friendly version of the unit name"
    )
    
    
    class Meta:
        indexes = [
            # Fast filtering by name
            models.Index(fields=['name' ]),
            models.Index(fields=['slug' ]),
 
        ]
        verbose_name = "Unit"
        verbose_name_plural = "Units"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name"""
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
            
        # Ensure slug uniqueness
        original_slug = self.slug
        counter = 1
        while Unit.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
            
        super().save(*args, **kwargs)

 