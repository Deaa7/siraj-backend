from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
# serializers :
from users.serializers import ResendOTPSerializer

# models
from .models import UserOTP
from users.models import User

# tasks
from .tasks import send_otp_email

# throttling
from rest_framework.throttling import ScopedRateThrottle

 
class resend_otp_view(APIView):
    
 # put a custom throttle decorator to limit the number of requests per minute
 throttle_classes = [ScopedRateThrottle]
 throttle_scope = "resend_otp"

 def post(self, request):
    """
    Endpoint to resend OTP for email verification or password reset
    Only allows resending if previous OTP is expired or doesn't exist
    """
        
    serializer = ResendOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    purpose = serializer.validated_data['purpose']

    try:
        # Get user by email
        user = get_object_or_404(User, email=email)
        
        if user.is_deleted:
            return Response(
                {
                    "error": "الحساب غير موجود",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Check if user is banned
        if user.is_banned:
            
            return Response(
                {"error": "الحساب محظور. السبب: " + (user.banning_reason or "غير محدد")},
                status=status.HTTP_403_FORBIDDEN
            )
            
        if user and user.is_email_confirmed:
         
         return Response({
            "error": "البريد الإلكتروني تم تأكيده بالفعل لذلك لا يمكن إعادة تعيين رمز التحقق"
         }, status=status.HTTP_400_BAD_REQUEST)
    
        
        # Check if there's already a valid (non-expired and unused) OTP for this purpose
        
        existing_otp = UserOTP.objects.filter(user=user, purpose=purpose, expire_at__gt=timezone.now(), is_used=False).first()
        
        if existing_otp:

            remaining_time = existing_otp.expire_at - timezone.now()
            total_seconds = int(remaining_time.total_seconds())
            remaining_minutes = total_seconds // 60
            remaining_seconds = total_seconds % 60
            
            if remaining_minutes > 0:
                if remaining_seconds > 0:
                    time_display = f"{remaining_minutes} دقيقة و {remaining_seconds} ثانية"
                else:
                    time_display = f"{remaining_minutes} دقيقة"
            else:
                time_display = f"{remaining_seconds} ثانية"
            
            return Response({
                "message": "يوجد رمز تحقق صالح مسبقاً",
                "email": email,
                "purpose": purpose,
                "otp_expires_in": time_display,
                "otp_expires_in_seconds": total_seconds,
                "warning": "يرجى استخدام الرمز الحالي أو انتظار انتهاء صلاحيته قبل طلب رمز جديد"
            }, status=status.HTTP_200_OK)
        
        # generate otp code
        otp_code = UserOTP.generate_otp()
        expire_at = timezone.now() + timedelta(minutes=15)
        
        existing_otp.otp_code = otp_code
        existing_otp.expire_at = expire_at
        existing_otp.save()
        
        # Create and send new OTP
        otp_result = send_otp_email.delay(otp_code = otp_code, first_name = user.first_name, email = user.email, purpose=purpose)
        
        if otp_result.status == 'SUCCESS':
            
            purpose_message = "تأكيد البريد الإلكتروني" if purpose == "email_verification" else "إعادة تعيين كلمة المرور"
            
            return Response({
                "message": f"تم إرسال رمز تحقق جديد لـ {purpose_message}",
                "email": email,
                "purpose": purpose,
                "otp_expires_in": "15 دقيقة"
            }, status=status.HTTP_200_OK)
       
        else:
       
            return Response({
                "error": "فشل في إرسال رمز التحقق. يرجى المحاولة مرة أخرى"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except User.DoesNotExist:
   
        return Response({
            "error": "البريد الإلكتروني غير مسجل في النظام"
        }, status=status.HTTP_404_NOT_FOUND)
   
    except Exception as e:
   
        return Response({
            "error": f"حدث خطأ أثناء معالجة الطلب: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
