from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from dotenv import load_dotenv
import os 
from Constants import CLASSES_ARRAY , SUBJECT_NAMES_ARRAY , CITIES_ARRAY
from services.parameters_validator import validate_pagination_parameters

from userOTP.tasks import send_otp_email
# models : 
from .models import User
from teamProfile.models import TeamProfile
from userOTP.models import UserOTP
from followers.models import Followers
from publisherPlans.models import PublisherPlans
from discountCodes.models import DiscountCodes
from posts.models import Post
from comments.models import Comment
from transactions.models import Transactions
from notifications.models import Notifications
from studentSavedElements.models import StudentSavedElements
from studentPremiumContent.models import StudentPremiumContent
from studentProfile.models import StudentProfile
from teacherProfile.models import TeacherProfile
from studentProfile.models import StudentProfile
from studentSubjectTracking.models import StudentSubjectTracking

# serializers : 
from .serializers import (
    CheckResetPasswordOTPSerializer,
    TeacherRegistrationSerializer,
    StudentRegistrationSerializer,
    TeamRegistrationSerializer,
    LoginSerializer,
    AdminLoginSerializer,
    ResetPasswordSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
    UserResponseSerializer,
)
from teacherProfile.serializers import OwnTeacherProfileSerializer
from studentProfile.serializers import OwnStudentProfileSerializer
from teamProfile.serializers import OwnTeamProfileSerializer



load_dotenv()

@api_view(["POST"])
def teacher_register(request):
    # """
    # Endpoint for teacher registration only
    # Automatically sets account_type to 'teacher'
    # request is something like this (nested structure):
    # {
    #     "username": "johndoe",
    #     "email": "john@example.com",
    #     "first_name": "John",
    #     "last_name": "Doe",
    #     "account_type": "teacher",
    #     "phone": "+1234567890",
    #     "city":"homs",
    #     "gender":"M",
    #     "password": "securepassword",
    #     "password_confirm": "securepassword",
    #     "profile": {
    #     "studying_subjects": "Math",
    #     "Class": "12",
    #     }
    # }
    # """
   try:
    serializer = TeacherRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        # This creates both User and Profile
        user = serializer.save()
       
        # otp = UserOTP.objects.create(
        #     user=user,
        #     purpose="email_verification"
        # )
        # data = send_otp_email.delay(otp_code = otp.otp_code, first_name = user.first_name, email = user.email, purpose="email_verification")
        return Response(
            {
                "message": "تم إنشاء حساب المعلم بنجاح! ",
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
   except Exception as  e :
    print(e)
    return Response({"errors": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

@api_view(["POST"])
def team_register(request):
    # """
    # Endpoint for team registration only
    # Automatically sets account_type to 'team'
    # request is something like this (nested structure):
    # {
    #     "username": "johndoe",
    #     "email": "john@example.com",
    #     "first_name": "John",
    #     "last_name": "Doe",
    #     "account_type": "team",
    #     "phone": "+1234567890",
    #     "city":"homs",
    #     "password": "securepassword",
    #     "password_confirm": "securepassword",
    # }
    # """
    serializer = TeamRegistrationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    user = serializer.save()

    # print('here is parameters', user.id, user.first_name, user.email, "email_verification")
 

    return Response(
        {
            "message": "تم إنشاء حساب الفريق بنجاح! تم إرسال رمز التحقق إلى بريدك الإلكتروني",
            "email": user.email,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def student_register(request):
    # """
    # Endpoint for student registration only
    # Automatically sets account_type to 'student'
    #     request is something like this (nested structure):
    # {
    #     "username": "johndoe",
    #     "email": "john@example.com",
    #     "first_name": "John",
    #     "last_name": "Doe",
    #     "account_type": "student",
    #     "phone": "+1234567890",
    #     "city":"homs",
    #     "gender":"M",
    #     "password": "securepassword",
    #     "password_confirm": "securepassword",
    #     "profile": {
    #     "Class": "12",
    #     }
    # }
    # """

    serializer = StudentRegistrationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    # Create user and profile using serializer
    user = serializer.save()

    # Create and send OTP for email verification
    # create_and_send_otp(user, purpose="email_verification")

    return Response(
        {
            "message": "تم إنشاء حساب الطالب بنجاح! تم إرسال رمز التحقق إلى بريدك الإلكتروني",
            "email": user.email,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def login(request):
    """
    Login endpoint that returns JWT access and refresh tokens
    """
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():

        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    validated_data = serializer.validated_data
    username = validated_data["username"]
    password = validated_data["password"]

    try:
        # Try to find user by username or email
        user = User.objects.filter(
            models.Q(username=username) | models.Q(email=username) | models.Q(phone=username)
        ).first()

        if not user or user.is_deleted:
            return Response(
                {"error": "اسم المستخدم أو البريد الإلكتروني أو الهاتف غير صحيح"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Verify password
        if not check_password(password, user.password):
            return Response(
                {"error": "كلمة المرور غير صحيحة"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
 
        if user.account_type == "student":
            studentData = StudentProfile.objects.select_related("user").get(user=user)
            # profile_data = OwnStudentProfileSerializer(studentData).data
        elif user.account_type == "team":
            teamData = TeamProfile.objects.select_related("user").get(user=user)
            # profile_data = OwnTeamProfileSerializer(teamData).data
        elif user.account_type == "teacher":
            teacherData = TeacherProfile.objects.select_related("user").get(user=user)
            # profile_data = OwnTeacherProfileSerializer(teacherData).data

        if not user.is_account_confirmed:
           # first check if there is any valid otp code , if not then create one 
           otp = UserOTP.objects.filter(user=user, purpose="email_verification", is_valid=True).first()
           if not otp:
               otp = UserOTP.objects.create(user=user, purpose="email_verification")
               send_otp_email.delay(otp_code = otp.otp_code, first_name = user.first_name, email = user.email, purpose="email_verification")
               return Response(
                   {
                       "message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني",
                       "email": user.email,
                   },
                   status=status.HTTP_200_OK
               )
     
        verified = False
        if user.account_type == "teacher":
                verified = teacherData.verified
        elif user.account_type == "team":
                verified = teamData.verified
       
        studying_subjects = None
        if user.account_type == "teacher":  
            studying_subjects = teacherData.studying_subjects
       
        Class = None
        if user.account_type == "teacher":
            Class = teacherData.Class
        elif user.account_type == "student":
            Class = studentData.Class
         # Create response
        response = Response(
                {
                    'message': 'تم تسجيل الدخول بنجاح',
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'user': {
                        "publicId": user.uuid,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "fullName": user.full_name,
                        "email": user.email,
                        "phone": user.phone,
                        "city": user.city,
                        "gender": user.gender,
                        "image": user.image,
                        "isBanned": user.is_banned,
                        "verified": verified,
                        "isAccountConfirmed": user.is_account_confirmed,
                        "accountType": user.account_type,
                        "balance": user.balance,
                        "Class": Class,
                        "studyingSubject": studying_subjects,
                    },
                },
                status=status.HTTP_200_OK
            )
        return response

    except Exception as e:
        return Response(
            {"error": f"حدث خطأ أثناء تسجيل الدخول: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

 
@api_view(["POST"])
def publisher_login(request):
    """
    Publisher login endpoint that returns JWT access and refresh tokens
    """
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():

        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    validated_data = serializer.validated_data
    username = validated_data["username"]
    password = validated_data["password"]

    try:
        # Try to find user by username or email
        user = User.objects.get(
            models.Q(username=username) | models.Q(email=username))

        if not user or user.is_deleted:
            return Response(
                {"error": "اسم المستخدم أو البريد الإلكتروني غير صحيح"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Verify password
        if not check_password(password, user.password):
            return Response(
                {"error": "كلمة المرور غير صحيحة"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if user.account_type not in ["teacher" , "team"]:
            return Response(
                {"error": "ليس لديك صلاحية للوصول إلى لوحة التحكم"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
 
        if user.account_type == "team":
            teamData = TeamProfile.objects.select_related("user").get(user=user)
        elif user.account_type == "teacher":
            teacherData = TeacherProfile.objects.select_related("user").get(user=user)
            
        studying_subjects = None
        if user.account_type == "teacher":  
            studying_subjects = teacherData.studying_subjects
      
        Class = None
        if user.account_type == "teacher":
            Class = teacherData.Class
        
        # Get verified status
        verified = False 
        if user.account_type == "teacher":
            verified = teacherData.verified
        elif user.account_type == "team":
            verified = teamData.verified    
         
        
        if not user.is_account_confirmed : 
            
             existing_otp = UserOTP.objects.filter(user=user, purpose="email_verification", expire_at__gt=timezone.now(), is_used=False).first()
             
             if not existing_otp : 
              otp =  UserOTP.objects.create(user=user, purpose="email_verification", expire_at=timezone.now() + timezone.timedelta(minutes=15) , otp_code=UserOTP.generate_otp())      
              send_otp_email.delay(otp_code = otp.otp_code, first_name = user.first_name, email = user.email, purpose="email_verification")
     
        response = Response(
                {
                    'message': 'تم تسجيل الدخول بنجاح',
                    'access_token': str(refresh.access_token),
                    'user': {
                        "publicId": user.uuid,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "fullName": user.full_name,
                        "email": user.email,
                        "phone": user.phone,
                        "city": user.city,
                        "gender": user.gender,
                        "image": user.image,
                        "isBanned": user.is_banned,
                        "verified": verified,
                        "isAccountConfirmed": user.is_account_confirmed,
                        "accountType": user.account_type,
                        "balance": user.balance,
                        "Class": Class,
                        "studyingSubject": studying_subjects,
                    },
                },
                status=status.HTTP_200_OK
            )
        
        response.set_cookie(    
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="None",  # 'Lax' allows cookies in cross-site requests
                max_age=30 * 24 * 60 * 60,  # 30 days in seconds
                path='/',  # Available for all paths
            )

        return response
    
    except Exception as e:
        return Response(
            {"error": f"حدث خطأ أثناء تسجيل الدخول: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def admin_login(request):
    """
    Admin login endpoint that returns JWT access and refresh tokens
    """
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():

        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    validated_data = serializer.validated_data
    username = validated_data["username"]
    password = validated_data["password"]

    try:
        # Try to find user by username or email
        user = User.objects.get(
            models.Q(username=username) | models.Q(email=username))

        if not user or user.is_deleted:
            return Response(
                {"error": "اسم المستخدم أو البريد الإلكتروني غير صحيح"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Verify password
        if not check_password(password, user.password):
            return Response(
                {"error": "كلمة المرور غير صحيحة"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if user.account_type != "admin":
            return Response(
                {"error": "ليس لديك صلاحية للوصول إلى لوحة الإدارة"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
 
 
   
        response = Response(
                {
                    'message': 'تم تسجيل الدخول بنجاح',
                    'access_token': str(refresh.access_token),
                    'user': {
                        "publicId": user.uuid,
                        "username": user.username,
                        "fullName": user.full_name,
                        "email": user.email,
                        "accountType": user.account_type,
                    },
                },
                status=status.HTTP_200_OK
            )
        
        response.set_cookie(    
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="None",  # 'Lax' allows cookies in cross-site requests
                max_age=30 * 24 * 60 * 60,  # 30 days in seconds
                path='/',  # Available for all paths
            )

        return response
    
    except Exception as e:
        return Response(
            {"error": f"حدث خطأ أثناء تسجيل الدخول: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def logout(request):
  
    """
    Logout endpoint that deletes refresh token cookie
    """
  
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookie or request body"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    token = RefreshToken(refresh_token)
    token.blacklist()

    response = Response(status=status.HTTP_200_OK)
    # Delete cookie with same path and settings as when it was set
    response.delete_cookie(
        key="refresh_token",
        path="/",  # Match the path used when setting the cookie
        samesite="Lax"  # Match the samesite setting
    )
  
    return response

@api_view(["POST"])
def refresh_token(request):
    """
    Refresh access token endpoint using refresh token
    Returns new access token and user information
    """
    # Debug: Print all cookies received
  
    refresh_token = request.COOKIES.get("refresh_token")
    
    # serializer = RefreshTokenSerializer(data={"refresh": refresh_token})
    # Check if refresh token exists in cookie
    if not refresh_token:
        # Also try to get from request body as fallback
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token not found in cookie or request body"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    # if not serializer.is_valid():
    #     return Response(
    #         {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
    #     )

    # refresh_token = serializer.validated_data["refresh"]
    # refresh_token

    try:
        # Verify and decode refresh token
        refresh = RefreshToken(refresh_token)
        # user = refresh.user
        user = User.objects.get(id=refresh.payload["user_id"])
        
        # Generate new access token
        new_access_token = refresh.access_token

        if user.account_type == "student":
            studentData = StudentProfile.objects.select_related("user").get(user=user)
            profile_data = OwnStudentProfileSerializer(studentData).data
        elif user.account_type == "team":
            teamData = TeamProfile.objects.select_related("user").get(user=user)
            profile_data = OwnTeamProfileSerializer(teamData).data
        elif user.account_type == "teacher":
            teacherData = TeacherProfile.objects.select_related("user").get(user=user)
            profile_data = OwnTeacherProfileSerializer(teacherData).data

        verified = False 
        if user.account_type == "teacher":
            verified = teacherData.verified
        elif user.account_type == "team":
            verified = teamData.verified
            
        studying_subjects = None
        if user.account_type == "teacher":  
            studying_subjects = teacherData.studying_subjects
        Class = None
        if user.account_type == "teacher":
            Class = teacherData.Class
        response_data = {
            "message": "تم تحديث رمز الوصول بنجاح",
            "access_token": str(new_access_token),
                   'user': {
                        "publicId": user.uuid,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "fullName": user.full_name,
                        "email": user.email,
                        "phone": user.phone,
                        "city": user.city,
                        "gender": user.gender,
                        "image": user.image,
                        "isBanned": user.is_banned,
                        "verified": verified,
                        "isAccountConfirmed": user.is_account_confirmed,
                        "accountType": user.account_type,
                        "balance": user.balance,
                        "Class": Class,
                        "studyingSubject": studying_subjects,
                    },
        }
        response_object = Response(response_data, status=status.HTTP_200_OK)
        response_object.set_cookie(
            key="refresh_token", 
            value=str(refresh), 
            httponly=True, 
            secure=True,  # Set to True in production (HTTPS only)
            samesite="None",  # 'Lax' allows cookies in cross-site requests
            path="/",  # Available for all paths
            max_age=60 * 60 * 24 * 30  # 30 days in seconds
        )
        return response_object

    except Exception as e:
        return Response(
            {"error": f"رمز التحديث غير صحيح أو منتهي الصلاحية: {str(e)}"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
def generate_reset_password_otp(request):
    """
    Endpoint for reset password functionality
    Checks if email exists and sends OTP code
    """
    serializer = ResetPasswordSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    email = serializer.validated_data["email"]

    try:
        # Get user by email
        user = User.objects.get(email=email)

        # Check if user is banned
        if user.is_banned:
            return Response(
                {
                    "error": "تم حظر حسابك. السبب: "
                    + (user.banning_reason or "غير محدد")
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if there's already a valid (non-expired and unused) OTP for password reset
        
        # check if there is a valid otp for this user and purpose
       
        otp = UserOTP.objects.filter(user=user, purpose="password_reset", is_used=False, expire_at__gt=timezone.now()).first()
        if otp:
            # Calculate remaining time
            remaining_time = otp.expire_at - timezone.now()
            total_seconds = int(remaining_time.total_seconds())
            remaining_minutes = total_seconds // 60
            remaining_seconds = total_seconds % 60

            # Format time display
            if remaining_minutes > 0:
                if remaining_seconds > 0:
                    time_display = (
                        f"{remaining_minutes} دقيقة و {remaining_seconds} ثانية"
                    )
                else:
                    time_display = f"{remaining_minutes} دقيقة"
            return Response(
                {"message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني مسبقاً", "email": email, "otp_expires_in": time_display, "otp_expires_in_seconds": total_seconds},
                status=status.HTTP_200_OK,
            )
        
        
        
        otp = UserOTP.objects.create(user=user, purpose="password_reset", expire_at=timezone.now() + timezone.timedelta(minutes=15) , otp_code=UserOTP.generate_otp() )
            
        send_otp_email.delay(otp_code = otp.otp_code, first_name = user.first_name, email = user.email, purpose="password_reset")
         
 
        return Response(
            {"message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني", "email": email, "otp_expires_in": "15 دقيقة", "otp_expires_in_seconds": 900, "otp_code": otp.otp_code},
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return Response(
            {"error": "البريد الإلكتروني غير مسجل في النظام"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": f"حدث خطأ أثناء معالجة الطلب: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def check_reset_password_otp(request) : 
    serializer = CheckResetPasswordOTPSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
    otp_code = serializer.validated_data["otp_code"]  
        # Find the OTP for this user and purpose
    otp = UserOTP.objects.filter(
            purpose="password_reset",
            otp_code=otp_code,
            is_used=False,
            expire_at__gt=timezone.now(),
        ).first()
    if otp:
            otp.delete()
            return Response({"message": "رمز التحقق صحيح"}, status=status.HTTP_200_OK)
    else:
            return Response({"error": "رمز التحقق غير صحيح أو منتهي الصلاحية"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def password_reset_confirm(request):
    """
    Endpoint for password reset confirmation
    Validates OTP code and updates user password
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    email = serializer.validated_data["email"]
    new_password = serializer.validated_data["new_password"]

    try:
        # Get user by email
        user = User.objects.get(email=email)

        # Check if user is banned
        if user.is_banned:
            return Response(
                {
                    "error": "تم حظر حسابك. السبب: "
                    + (user.banning_reason or "غير محدد")
                },
                status=status.HTTP_403_FORBIDDEN,
            )
   
        # Update user password
        user.password = make_password(new_password)
        user.save()

   
        return Response(
            {"message": "تم تغيير كلمة المرور بنجاح"}, status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        return Response(
            {"error": "البريد الإلكتروني غير مسجل في النظام"},
            status=status.HTTP_404_NOT_FOUND,
        )
        
    except Exception as e:
        return Response(
            {"error": f"حدث خطأ أثناء معالجة الطلب: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
 
class verify_account(APIView):
    
   throttle_classes = [ScopedRateThrottle]
   throttle_scope = "verify_account"
   def post(self, request):
    """
    Endpoint for email verification
    Validates OTP code and marks user as verified
    """
    serializer = EmailVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    email = serializer.validated_data["email"]
    otp_code = serializer.validated_data["otp_code"]
    

    try:
        # Get user by email
        user = User.objects.get(email=email)

        if user.is_deleted:
            return Response(
                {
                    "message": "الحساب غير موجود",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
            
        # Check if user is banned
        if user.is_banned:
            return Response(
                {
                    "error": "الحساب محظور. السبب: "
                    + (user.banning_reason or "غير محدد")
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if user is already verified
        if user.is_account_confirmed:
            return Response(
                {
                    "message": "تم تأكيد حسابك مسبقاً",
                    "email": email,
                    "already_verified": True,
                },
                status=status.HTTP_200_OK,
            )

        # Find the OTP for this user and purpose
        otp = UserOTP.objects.filter(
            user=user,
            purpose="email_verification",
            otp_code=otp_code,
            is_used=False,
            expire_at__gt=timezone.now(),
        ).first()

        if not otp:
            return Response(
                {"error": "رمز التحقق غير صحيح أو منتهي الصلاحية"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete the OTP after successful validation
        otp.delete()

        # Mark user as verified
        user.is_account_confirmed = True
        user.save()


        return Response(
            {"message": "تم تأكيد حسابك بنجاح", "email": email, "verified": True},
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return Response(
            {"error": "البريد الإلكتروني غير مسجل في النظام"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": f"حدث خطأ أثناء معالجة الطلب: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@permission_classes([IsAuthenticated])
@api_view(["DELETE"])
def delete_account(request):
    """
      Endpoint for deleting account
      what is the type of the user ?
     
      teacher / team : 
      profile , post , comment ,notification , followers ( followed_id ) ,publisher_plan ,
      discount_code 
     
      stduent : 
     
      profile , comment , notification , saved_elements , premium_content ,
    """
    user = request.user
 
    user.deleted_reason = f"قام {user.first_name} {user.last_name} بحذف حسابه"

    user.username = f"deleted_{user.id}"
    user.first_name = "حساب محذوف"
    user.last_name = ""
    user.full_name = ""
    user.team_name = ""
    user.is_deleted = True
    user.is_banned = True
    user.banning_reason = "حذف الحساب"
    user.is_account_confirmed = False
    
    user.email = f"deleted_{user.id}@siraj.sy"
    
    new_phone = str(user.id)
    while len(new_phone) < 10 :
        new_phone +="0"
    user.phone = new_phone
    user.image = ""
    
    owner_id = os.getenv("OWNER_ID")
    
    owner = User.objects.get(id=owner_id)
    owner.balance += user.balance
    owner.save()    
    
    user.balance = 0
    
    user.password = make_password(f"deleted_password_{user.id}")
    
    user.save()
    
    if user.account_type in ["teacher", "team"]:
        
        if user.account_type == "teacher":
         teacher_profile = TeacherProfile.objects.get(user=user)
         teacher_profile.delete()
       
        else :
         team_profile = TeamProfile.objects.get(user=user)
         team_profile.delete()
            
        notifications = Notifications.objects.filter(receiver_id=user)
        notifications.delete()
      
        followers = Followers.objects.filter(followed_id=user)
        followers.delete()
      
        followers_teacher = Followers.objects.filter(follower_id=user)
        followers_teacher.delete()
        
        publisher_plan = PublisherPlans.objects.filter(user=user)
        publisher_plan.delete()
      
        discount_code = DiscountCodes.objects.filter(publisher_id=user)
        discount_code.delete()
        
        posts = Post.objects.filter(user=user)
        posts.delete()
        
        comments = Comment.objects.filter(user_id=user)
        comments.delete()
        
        
    elif user.account_type == "student":
        
        student_profile = StudentProfile.objects.get(user=user)
        student_profile.delete()
        
        comments = Comment.objects.filter(user=user)
        comments.delete()
        
        notifications = Notifications.objects.filter(receiver_id=user)
        notifications.delete()
        
        saved_elements = StudentSavedElements.objects.filter(user=user)
        saved_elements.delete()
        
        premium_content = StudentPremiumContent.objects.filter(user=user)
        premium_content.delete()
        
        subject_tracking = StudentSubjectTracking.objects.filter(user=user)
        subject_tracking.delete()

    return Response({"message": "تم حذف حسابك بنجاح"}, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_publisher_cards(request):
    
    user_type = request.query_params.get("user_type" , "teacher")
    order_by = request.query_params.get("order_by" , "number_of_followers")
    Class = request.query_params.get("Class" , "all")
    subject_name = request.query_params.get("subject_name" , "all")
    city = request.query_params.get("city" , "all")
    
    if user_type not in ["teacher", "team"]:
        return Response({"error": "نوع الحساب غير معروف"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate city (make it optional)
    if city != "all" and city not in CITIES_ARRAY:
        return Response({"error": "المدينة غير معروفة"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate Class (only for teachers, make it optional)
    if user_type == "teacher" and Class != "all" and Class not in CLASSES_ARRAY:
        return Response({"error": "الصف غير معروف"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate subject_name (only for teachers, make it optional)
    if user_type == "teacher" and subject_name != "all" and subject_name not in SUBJECT_NAMES_ARRAY:
        return Response({"error": "المادة غير معروفة"}, status=status.HTTP_400_BAD_REQUEST)
    
    if order_by not in ["number_of_exams", "number_of_courses", "number_of_notes", "number_of_followers", "years_of_experience"]:
        return Response({"error": "الترتيب غير معروف"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate pagination parameters
    count, limit = validate_pagination_parameters(
        request.query_params.get("count", 0),
        request.query_params.get("limit", 7)
    )
    
    try:
        # Build base query filters
        base_filters = {
            "user__account_type": user_type,
            "user__is_deleted": False,
            "user__is_banned": False,
        }
        
        # Add city filter if provided
        if city and city != "all":
            base_filters["user__city"] = city
        
        # Query based on user_type
        if user_type == "teacher":
            # Add teacher-specific filters
            if Class and Class != "all":
                base_filters["Class"] = Class
            if subject_name and subject_name != "all":
                base_filters["studying_subjects"] = subject_name
            
            # Query teachers
            publishers = TeacherProfile.objects.filter(
                **base_filters
            ).select_related('user')
            
            # Apply ordering
            order_by_field = f"-{order_by}"
            publishers = publishers.order_by(order_by_field)
            
            # Get total count before pagination
            total_number = publishers.count()
            
            # Apply pagination
            begin = count * limit
            end = (count + 1) * limit
            
            # Check if begin/end exceed total_number and adjust
            if begin > total_number:
                begin = total_number
            if end > total_number:
                end = total_number
            
            # Slice the queryset
            publishers = publishers[begin:end]
            
            # Format response data using the same structure as most_popular_publishers
            response_data = []
            for publisher in publishers:
                # Format the name based on publisher type and gender
                user = publisher.user
                if user.gender == "M":
                    formatted_name = f"الاستاذ {user.full_name}"
                elif user.gender == "F":
                    formatted_name = f"الآنسة {user.full_name}"
                else:
                    formatted_name = user.full_name
                
                # Build response data
                formatted_data = {
                    "name": formatted_name,
                    "image": publisher.user.image,
                    "publisher_type": "teacher",
                    "public_id": str(publisher.user.uuid),
                    "city": publisher.user.city,
                    "number_of_exams": publisher.number_of_exams,
                    "number_of_notes": publisher.number_of_notes,
                    "number_of_courses": publisher.number_of_courses,
                    "number_of_followers": publisher.number_of_followers,
                    "experience_years": publisher.years_of_experience if publisher.years_of_experience else None,
                    "address": publisher.address if publisher.address else None,
                    "subject_name": publisher.studying_subjects if publisher.studying_subjects else None,
                    "Class": publisher.Class if publisher.Class else None,
                    "university": publisher.university if publisher.university else None,
                }
                response_data.append(formatted_data)
        
        else:  # team
            # Query teams (Class and subject_name don't apply to teams)
            publishers = TeamProfile.objects.filter(
                **base_filters
            ).select_related('user')
            
            # Apply ordering
            order_by_field = f"-{order_by}"
            publishers = publishers.order_by(order_by_field)
            
            # Get total count before pagination
            total_number = publishers.count()
            
            # Apply pagination
            begin = count * limit
            end = (count + 1) * limit
            
            # Check if begin/end exceed total_number and adjust
            if begin > total_number:
                begin = total_number
            if end > total_number:
                end = total_number
            
            # Slice the queryset
            publishers = publishers[begin:end]
            
            # Format response data
            response_data = []
            for publisher in publishers:
                # Format the name for team
                formatted_name = f"فريق {publisher.user.team_name}"
                
                # Build response data
                formatted_data = {
                    "name": formatted_name,
                    "image": publisher.user.image,
                    "publisher_type": "team",
                    "public_id": str(publisher.user.uuid),
                    "city": publisher.user.city,
                    "number_of_exams": publisher.number_of_exams,
                    "number_of_notes": publisher.number_of_notes,
                    "number_of_courses": publisher.number_of_courses,
                    "number_of_followers": publisher.number_of_followers,
                    "experience_years": publisher.years_of_experience if publisher.years_of_experience else None,
                    "address": publisher.address if publisher.address else None,
                    "subject_name": None,
                    "Class": None,
                    "university": None,
                }
                response_data.append(formatted_data)
        
        # Return response with pagination info
        return Response({
            "publishers": response_data,
            "total_number": total_number
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )




