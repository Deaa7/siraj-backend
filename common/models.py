from django.db import models
import uuid

class PublicModel(models.Model):
    """
    Base model with common public fields
    """
    public_id = models.CharField(
        max_length=35,
        unique=True,
        db_index=True,
        editable=False,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
   
    class Meta:
        abstract = True
        ordering = ['-created_at']  # ← This does the magic!
        indexes = [
            models.Index(fields=['-created_at']),  # ← This makes it fast
        ]
        
    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = self.generate_public_id()
        super().save(*args, **kwargs)
    
    def generate_public_id(self, short_length=15):
        """
        Generate public ID with UUID fallback for collision handling
        Strategy: Try short codes first, fallback to UUID if needed
        """
        # Try short codes first (for readability)
        short_code = self._generate_short_code(short_length)
        if short_code:
            return short_code
        
        # Fallback to UUID (guaranteed unique)
        uuid_fallback = self._generate_uuid_fallback()
        return uuid_fallback
    
    def _generate_short_code(self, length=15, max_attempts=100):
      
        
        for attempt in range(max_attempts):
            candidate =  uuid.uuid4().hex[:length]  
            candidate = candidate.upper()
            
            # Check if this public_id already exists
            if not self.__class__.objects.filter(public_id=candidate).exists():
                return candidate
        
        # No unique short code found
        return None
    
    def _generate_uuid_fallback(self):
        """
        Generate UUID-based fallback ID
        Using first N characters of UUID4 (guaranteed unique enough)
        """
        while True:
            # Generate full UUID and take first N characters
            full_uuid = uuid.uuid4().hex  # 32 character hex string
            candidate = full_uuid.upper()
            candidate = candidate.replace("-", "")
            
            
            # Double-check uniqueness (extremely rare but safe)
            if not self.__class__.objects.filter(public_id=candidate).exists():
                return candidate