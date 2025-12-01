"""
URL configuration for Siraj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
      
    path('api/admin-app/', include('adminApp.urls')),

   # users
    path('api/users/', include('users.urls')),
    path('api/otp/', include('userOTP.urls')),
    path('api/followers/' , include('followers.urls')),
    path('api/reports/', include('reports.urls')),

    #exams
    path('api/exams/', include('exams.urls')),
    path('api/exam-tracking/' , include('examAppTracking.urls')),
    path('api/mcq/', include('MCQ.urls')),
    
    path('api/notes/', include('notes.urls')),
    path('api/note-appendixes/', include('notesAppendixes.urls')),
    path('api/note-tracking/' , include('noteReadTracking.urls')),

    #courses
    path('api/courses/', include('courses.urls')),
    path('api/course-tracking/' , include('courseStatusTracking.urls')),
   
    #social
    path('api/posts/', include('posts.urls')),
    path('api/comments/', include('comments.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    #financial
    path('api/charging-orders/', include('chargingOrders.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/purchase-history/', include('purchaseHistory.urls')),
    path('api/withdraw-balance-request/', include('withdrawBalanceRequest.urls')),
    path('api/discount-codes/', include('discountCodes.urls')),
    
    #students
    path('api/student/', include('studentProfile.urls')),
    path('api/student-premium-content/', include('studentPremiumContent.urls')),
    path('api/student-subject-tracking/', include('studentSubjectTracking.urls')),
    path('api/student-saved-elements/', include('studentSavedElements.urls')),

    #publishers
    path('api/teacher/', include('teacherProfile.urls')),
    path('api/team/', include('teamProfile.urls')),
    path('api/publisher-plans/', include('publisherPlans.urls')),
    path('api/publisher-verification-requests/', include('publisherVerificationRequests.urls')),
    #common
    path('api/common/', include('common.urls')),
    
    #telegram
    # path('api/telegram/', include('telegramBot.urls')),

]

 