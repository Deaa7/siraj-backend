from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from premailer import transform


@shared_task(bind=True)
def send_otp_email(
    self,
    otp_code,
    first_name,
    email="example@example.com",
    purpose="email_verification",
):
    """
    Async function to send OTP email to user
    """
    try:
        context = {
        'user_name': first_name,
        'otp_code': otp_code,
        'otp_expiry': 15,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
        'support_email': settings.SUPPORT_EMAIL,
    }
        
        if purpose == 'email_verification':
            subject = f"تأكيد بريدك الإلكتروني - {settings.SITE_NAME}"
            template_name = 'emails/email_verification.html'
        elif purpose == 'password_reset':
            subject = f"إعادة تعيين كلمة المرور - {settings.SITE_NAME}"
            template_name = 'emails/password_reset.html'
        else:
            raise ValueError("Invalid purpose")
        
        # عرض محتوى HTML
        html_content = render_to_string(template_name, context)
        
        final_html = transform(html_content)
        
        # text_content = strip_tags(html_content)  # إزالة الوسوم للإصدار النصي العادي
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=final_html,
            # subject='Test',
            # body='<h1>Test HTML</h1>',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email.content_subtype = "html"  # Set content type to HTML
        
        # Send email
        email.send()
        return {
            "success": True,
            "message": "تم إرسال رمز التحقق بنجاح",
        }

    except Exception as e:
        
        return {
            "success": False,
            "message": f"فشل في إنشاء رمز التحقق: {str(e)}",
            "otp": otp_code,
        }

