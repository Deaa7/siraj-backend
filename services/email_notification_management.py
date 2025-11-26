
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def withdraw_balance_request_confirmed(full_name , email , amount , payment_way  ,confirmation_date):
    
 subject = "إشعار إتمام عملية سحب رصيد"
 
 

# def send_otp_email_async(user, profile, otp_code, purpose="email_verification"):
#     """
#     Async function to send OTP email to user
#     """
    
#     try:
        
#         context = {
#         'user_name': user.first_name,
#         'otp_code': otp_code,
#         'otp_expiry': 15,
#         'site_name': settings.SITE_NAME,
#         'site_url': settings.SITE_URL,
#         'support_email': settings.SUPPORT_EMAIL,
#     }
        
#         if purpose == 'email_verification':
       
#             subject = f"تأكيد بريدك الإلكتروني - {settings.SITE_NAME}"
#             template_name = 'emails/email_verification_ar.html'
       
#         elif purpose == 'password_reset':
       
#             subject = f"إعادة تعيين كلمة المرور - {settings.SITE_NAME}"
#             template_name = 'emails/password_reset_ar.html'
       
#         else:
       
#             raise ValueError("Invalid purpose")
        
#         # عرض محتوى HTML
#         html_content = render_to_string(template_name, context)
#         text_content = strip_tags(html_content)  # إزالة الوسوم للإصدار النصي العادي
        
    
#         # # Different email content based on purpose
#         # if purpose == "password_reset":
#         #     subject = "رمز التحقق - إعادة تعيين كلمة المرور"
#         #     html_message = f"""
#         #     <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
#         #         <h2 style="color: #2c3e50; text-align: center;">مرحباً {profile.first_name}</h2>
                
#         #         <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
#         #             <h3 style="color: #34495e; text-align: center;">رمز التحقق لإعادة تعيين كلمة المرور</h3>
#         #             <div style="background-color: #e74c3c; color: white; padding: 15px; text-align: center; border-radius: 5px; font-size: 24px; font-weight: bold; margin: 15px 0;">
#         #                 {otp_code}
#         #             </div>
#         #             <p style="text-align: center; color: #7f8c8d;">
#         #                 استخدم هذا الرمز لإعادة تعيين كلمة المرور الخاصة بك. هذا الرمز صالح لمدة 15 دقيقة فقط.
#         #             </p>
#         #         </div>
                
#         #         <div style="background-color: #e74c3c; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
#         #             <h4 style="margin: 0;">تحذير أمني:</h4>
#         #             <ul style="margin: 10px 0;">
#         #                 <li>لا تشارك هذا الرمز مع أي شخص آخر</li>
#         #                 <li>إذا لم تطلب إعادة تعيين كلمة المرور، يرجى تجاهل هذا البريد</li>
#         #                 <li>سيتم حذف هذا الرمز تلقائياً بعد انتهاء صلاحيته</li>
#         #             </ul>
#         #         </div>
                
#         #         <div style="text-align: center; margin-top: 30px; color: #95a5a6;">
#         #             <p>إذا كنت بحاجة إلى مساعدة، يرجى التواصل مع فريق الدعم</p>
#         #             <p>فريق سراج التعليمي</p>
#         #         </div>
#         #     </div>
#         #     """
#         # else:
#         #     # Default email verification content
#         #     subject = "رمز التحقق - تأكيد الحساب"
#         #     html_message = f"""
#         #     <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
#         #         <h2 style="color: #2c3e50; text-align: center;">مرحباً {user.first_name}</h2>
                
#         #         <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
#         #             <h3 style="color: #34495e; text-align: center;">رمز التحقق الخاص بك</h3>
#         #             <div style="background-color: #3498db; color: white; padding: 15px; text-align: center; border-radius: 5px; font-size: 24px; font-weight: bold; margin: 15px 0;">
#         #                 {otp_code}
#         #             </div>
#         #             <p style="text-align: center; color: #7f8c8d;">
#         #                 استخدم هذا الرمز لتأكيد حسابك. هذا الرمز صالح لمدة 15 دقيقة فقط.
#         #             </p>
#         #         </div>
                
#         #         <div style="background-color: #e74c3c; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
#         #             <h4 style="margin: 0;">تحذير أمني:</h4>
#         #             <ul style="margin: 10px 0;">
#         #                 <li>لا تشارك هذا الرمز مع أي شخص آخر</li>
#         #                 <li>إذا لم تطلب هذا الرمز، يرجى تجاهل هذا البريد</li>
#         #                 <li>سيتم حذف هذا الرمز تلقائياً بعد انتهاء صلاحيته</li>
#         #             </ul>
#         #         </div>
                
#         #         <div style="text-align: center; margin-top: 30px; color: #95a5a6;">
#         #             <p>شكراً لانضمامك إلى منصتنا التعليمية</p>
#         #             <p>فريق سراج التعليمي</p>
#         #         </div>
#         #     </div>
#         #     """
        
#         # Create email message
#         email = EmailMessage(
#             subject=subject,
#             body=text_content,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[user.email],
#         )
#         email.content_subtype = "html"  # Set content type to HTML
        
#         # Send email
#         email.send()
        
#         return True
        
#     except Exception as e:
#         return False

