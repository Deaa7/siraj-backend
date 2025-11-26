from celery import shared_task
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage


@shared_task(bind=True)
def charging_order_success_email_notification(self , email , full_name , amount , transaction_public_id ):
    """
    Send email notification to user when charging order is validated
    """
    try:
        context = {
        'full_name': full_name,
        'amount': amount,
        'transaction_id': transaction_public_id,
        'date_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
        
        subject = f"شحن رصيد بنجاح - {settings.SITE_NAME}"
        template_name = 'emails/balance_charged.html'
        
        # عرض محتوى HTML
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)  # إزالة الوسوم للإصدار النصي العادي
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email.content_subtype = "html"  # Set content type to HTML
        
        # Send email
        email.send()
        return {
            "success": True,
            "message": "تم إرسال البريد الإلكتروني بنجاح",
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"فشل في إرسال البريد الإلكتروني: {str(e)}",
        }


