
from celery import shared_task

# models
from .models import Notifications
from exams.models import Exam
from followers.models import Followers
from courses.models import Course
from notes.models import Note
from posts.models import Post
from comments.models import Comment


@shared_task(bind=True)
def publishing_exam_notification(self, exam_id = 0 , user = None ):

    if user is None:
        return
    
    exam = Exam.objects.get(id=exam_id)
    
    if exam is None:
        return
    
    followers = Followers.objects.filter(followed_id=user.id).values_list('follower_id' , flat=True).iterator()
    
    for follower in followers:
        Notifications.objects.create(
            receiver_id=follower,
            source_id=exam.public_id,
            source_type="exam",
            title=" اختبار جديد",
            content=f"تم نشر اختبار جديد {exam.name} من قبل {user.full_name}",
        )

@shared_task(bind=True)
def publishing_course_notification(self, course_id = 0 , user = None ):

    if user is None:
        return

    course = Course.objects.get(id=course_id)
    if course is None:
        return
    
    followers = Followers.objects.filter(followed_id=user.id).values_list('follower_id' , flat=True).iterator()

    for follower in followers:
        Notifications.objects.create(
            receiver_id=follower,
            source_id=course.public_id,
            source_type="course",
            title=" دورة جديدة",
            content=f"تم نشر دورة جديدة {course.name} من قبل {user.full_name}",
        )


@shared_task(bind=True)
def publishing_note_notification(self, note_id = 0 , user = None , name = "" ):
 
    if user is None:
        return

    note = Note.objects.get(id=note_id)
    if note is None:
        return
    
    followers = Followers.objects.filter(followed_id=user).values_list('follower_id' , flat=True).iterator()

    for follower in followers:
        Notifications.objects.create(
            receiver_id=follower,
            source_id=note.public_id,
            source_type="note",
            title=" نوطة جديدة",
            content=f"تم نشر نوطة جديدة {note.name} من قبل {name}",
        )


@shared_task(bind=True)
def publishing_post_notification(self, post_id=0, user=None):

    if user is None:
        return

    post = Post.objects.get(id=post_id)
    if post is None:
        return

    followers = Followers.objects.filter(followed_id=user.id).values_list('follower_id', flat=True).iterator()

    for follower in followers:
        Notifications.objects.create(
            receiver_id=follower,
            source_id=post.public_id,
            source_type="post",
            title="منشور جديد",
            content=f"قام {user.full_name} بنشر منشور جديد",
        )


@shared_task(bind=True)
def publishing_comment_notification(self, comment_id=0, user=None , content_type=None , content_public_id=None , content_name=None):

    if user is None:
        return
   
 
    followers = Followers.objects.filter(followed_id=user.id).values_list("follower_id", flat=True).iterator()

    notification_content = f"قام {user.full_name} بكتابة تعليق جديد على {content_type} {content_name}"

    for follower in followers:
        Notifications.objects.create(
            receiver_id=follower,
            source_type="comment",
            title="تعليق جديد",
            source_id=content_public_id,
            content=notification_content,
        )
@shared_task(bind=True)
def plan_renewal_notification(self, user, plan_name, plan_price):
   
    if user is None:
        return
    
    Notifications.objects.create(
        receiver_id=user.id,
        source_type="management",
        title="تجديد الباقة",
        content=f"تم تجديد {plan_name} بنجاح و خصم {plan_price} ل.س من رصيدك"
    )
    

@shared_task(bind=True)
def plan_expired_notification(self, user, plan_name):
  
    if user is None:
        return
    
    Notifications.objects.create(
        receiver_id=user.id,
        source_type="management",
        title="انتهاء الباقة",
        content=f"تم انتهاء {plan_name} و تعطيل بعض المحتويات بسبب انتهاء الباقة وعدم تجديدها"
    )
    
    
@shared_task(bind=True)
def successful_purchase_notification( student_id , content_type , content_type_arabic_name , content_id , content_name , price, publisher_name):
    
        Notifications.objects.create(
        receiver_id=student_id,
        source_type=content_type,
        source_id=content_id,
        title="شراء " + content_type_arabic_name,
        content="تم شراء "
        + content_type_arabic_name
        + " "
        + content_name
        + " بسعر "
        + str(price)
        + "ل.س "
        + " من "
        + publisher_name,
 
    )

