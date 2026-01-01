import bleach
import re
from django.core.exceptions import ValidationError

class SecurityValidator:
    # Tags allowed for math/content
    ALLOWED_TAGS = ['span', 'p', 'br', 'strong', 'em', 'u' , 'div' , 'li']
    # Attributes allowed for MathJax/LaTeX support
    ALLOWED_ATTRS = {'span': ['class', 'data-formula', 'style' , 'contenteditable' , 'id']}

    @classmethod
    def validate_input(cls, value, field_name="field"):
        if not isinstance(value, str) or not value:
            return value

        # 1. Detect active threats (Scripts/Events)
        danger_patterns = r"(<script|javascript:|onerror=|onload=|onclick=)"
        if re.search(danger_patterns, value.lower()):
            raise ValidationError(f"محتوى غير آمن في حقل {field_name}")

        # 2. Use bleach to clean HTML instead of html.escape()
        # This preserves characters like ' and " while stripping <script>
        cleaned = bleach.clean(
            value,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRS,
            strip=True
        )
        
        # 3. Unescape entities that bleach might have missed for simple text
        import html
        return html.unescape(cleaned).strip()

    @classmethod
    def validate_text_field(cls, value, field_name="field"):
        
        if value is None or (isinstance(value, str) and not value.strip()):
         return ""
        return cls.validate_input(value, field_name)