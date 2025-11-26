from datetime import timedelta
from dotenv import load_dotenv
from django.utils import timezone
import os
#tasks
from notifications.tasks import plan_expired_notification, plan_renewal_notification
#models 
from servicePurchaseHistory.models import ServicePurchaseHistory
from publisherOffers.models import PublisherOffers
from publisherPlans.models import PublisherPlans
from users.models import User
from teacherProfile.models import TeacherProfile
from teamProfile.models import TeamProfile
from exams.models import Exam
from notes.models import Note
from courses.models import Course

#services
from services.transaction_manager import record_transaction


load_dotenv()


def _ensure_aware(dt):
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def check_publisher_plan(publisher_id):

    # we get the current plan of the publisher
    plan = PublisherPlans.objects.get(user=publisher_id)

    now = timezone.now()
    expiration_date = _ensure_aware(plan.plan_expiration_date)

    # if the plan is free plan , or did not expire yet , then return
    if expiration_date is None or expiration_date >= now:
        return
    
    user = User.objects.get(id=publisher_id)

    publisher = None

    if user.account_category == "teacher":
        publisher = TeacherProfile.objects.get(user=publisher_id)
    
    elif user.account_category == "team":
        publisher = TeamProfile.objects.get(user=publisher_id)

    # if the plan is auto renew and the user has enough balance, then renew the plan
    if plan.auto_renew and user.balance >= plan.offer.offer_price:

        _auto_activate_offer(user.id)
    else:

        # if the plan is not auto renew and the user does not have enough balance, then disable the plan
        # and activate the free plan

        publisher_type = user.account_type       
        
        free_offer = PublisherOffers.objects.get(offer_for=publisher_type,offer_price = 0)
        
        plan.offer = free_offer

        plan.auto_renew = False
        plan.plan_expiration_date = None
        plan.save()

        res = _disable_extra_content(user , publisher, free_offer.number_of_exams)
        
        # send notification to publisher
        if res :
            plan_expired_notification.delay(user, free_offer.offer_name)
        
        publisher.number_of_exams = free_offer.number_of_exams
        publisher.number_of_notes = free_offer.number_of_notes
        publisher.number_of_courses = free_offer.number_of_courses
        publisher.save()

def _disable_extra_content(user, publisher, num):

    publisher_id = user.id

    disabled_anything = False

    if publisher.number_of_exams > num:
       
        disabled_anything = True
       
        exams = Exam.objects.filter(publisher_id=publisher_id)
       
        diff = publisher.number_of_exams - num

        for exam in exams:

            exam.active = False
            exam.disable_date = timezone.now()
            exam.disabled_by = "admin"
            exam.save()
            
            diff -= 1
            if diff <= 0:
                break

    if publisher.number_of_notes > num:
     
        disabled_anything = True
     
        notes = Note.objects.filter(publisher_id=publisher_id)
     
        diff = publisher.number_of_notes - num

        for note in notes:
            
            note.active = False
            note.disable_date = timezone.now()
            note.disabled_by = "admin"
            note.save()
            
            diff -= 1
            if diff <= 0:
                break

    if publisher.number_of_courses > num:
       
        disabled_anything = True
        
        courses = Course.objects.filter(publisher_id=publisher_id)

        for course in courses:
        
            course.active = False
            course.disable_date = timezone.now()
            course.disabled_by = "admin"
            course.save()

    return disabled_anything


def check_publishing_content_availability(publisher_id , publisher_type ,  content_type ):
    
    publisher = None 
    publisher_plan = PublisherPlans.objects.get(user=publisher_id)

    if publisher_plan is None:
        return False

    expiration = _ensure_aware(publisher_plan.plan_expiration_date)
    now = timezone.now()

    if expiration and expiration < now:
        
     if publisher_plan.auto_renew:
            _auto_activate_offer(publisher_id)
            publisher_plan = PublisherPlans.objects.get(user=publisher_id)
     else :
        return False
  
    if publisher_type == "teacher":
        publisher = TeacherProfile.objects.get(user=publisher_id)
    elif publisher_type == "team":
        publisher = TeamProfile.objects.get(user=publisher_id)
        
    if publisher is None:
        return False
    
    if content_type == "exam":
        return publisher.number_of_exams + 1 <= publisher_plan.offer.number_of_exams
    elif content_type == "note":
        return publisher.number_of_notes + 1 <= publisher_plan.offer.number_of_notes
    elif content_type == "course":
        return publisher.number_of_courses + 1 <= publisher_plan.offer.number_of_courses
    
    return False


def _auto_activate_offer(user_id) : 
    
 user = User.objects.get(id=user_id)
 publisher_plan = PublisherPlans.objects.get(user=user_id)
 
 if user is None:
    return False
 
 if user.account_type != "teacher" and user.account_type != "team":
    return False
 
 if publisher_plan is None or  publisher_plan.offer is None or publisher_plan.offer.active == False:
    return False
 
 if publisher_plan.offer.offer_price > user.balance:
    return False

 if not publisher_plan.auto_renew:
    return False

 publisher_plan.plan_expiration_date = timezone.now() + timedelta(days=30)
 publisher_plan.activation_date = timezone.now()
 publisher_plan.save()
        
 record_transaction(user.id, publisher_plan.offer.offer_price, "purchase" , "completed")
        
 user.balance -= publisher_plan.offer.offer_price
 user.save()

 owner = User.objects.get(id=os.getenv("OWNER_ID"))
        
 record_transaction(owner.id, publisher_plan.offer.offer_price, "purchase" , "completed")
 
 owner.balance += publisher_plan.offer.offer_price
 owner.save()
        
 ServicePurchaseHistory.objects.create(
     user_id=user.id,
     full_name=user.full_name,
     user_type=user.account_category,
     phone=user.phone,
     city=user.city,
     service_name=publisher_plan.plan_name,
     service_price=publisher_plan.offer.offer_price,
 )

  