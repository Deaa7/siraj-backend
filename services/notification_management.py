from notifications.models import Notifications
from comments.models import Comment


 

def publishing_comment_notification(comment_id):

    comment = Comment.objects.get(id=comment_id)

    content = ""
    content_id = None
    content_name = ""
    publisher_id = 1

    if comment.note_id is not None:
        content = "note"
        content_id = comment.note_id.id
        content_name = comment.note_id.name
        publisher_id = comment.note_id.publisher_id

    elif comment.exam_id is not None:
        content = "exam"
        content_id = comment.exam_id.id
        content_name = comment.exam_id.name
        publisher_id = comment.exam_id.publisher_id
        
    elif comment.course_id is not None:
        content = "course"
        content_id = comment.course_id.id
        content_name = comment.course_id.name
        publisher_id = comment.course_id.publisher_id
        
    elif comment.post_id is not None:
        content = "post"
        content_id = comment.post_id.id
        content_name = comment.post_id.content
        publisher_id = comment.post_id.publisher_id

    content_name = content_name[:10] + "..."

    if len(content_name) <= 10:
        content_name = content_name

    notification_content = ""
    if content == "exam":
        notification_content = f"تم نشر تعليق جديد على اختبار {content_name}"
    elif content == "note":
        notification_content = f"تم نشر تعليق جديد على نوطة {content_name}"
    elif content == "course":
        notification_content = f"تم نشر تعليق جديد على دورة {content_name}"
    elif content == "post":
        notification_content = f"تم نشر تعليق جديد على منشور {content_name}"

    Notifications.objects.create(
        receiver_id=publisher_id,
        source_id=content_id,
        source_type=content,
        title=" تعليق جديد",
        content=notification_content,
    )



 
    


def disable_content_by_admin_notification(publisher_id ,content_type , content_id , content_name):
    
    if len(content_name) > 10:
        content_name = content_name[:10] + "..."
 
        content_arabic_name = "الاختبار" if content_type == "exam" else "النوطة" if content_type == "note" else "الدورة" if content_type == "course" else ""
   
    Notifications.objects.create(
        receiver_id=publisher_id,
        source_type=content_type,
        source_id=content_id,
        title="تعطيل المحتوى",
        content=f"تم تعطيل {content_arabic_name} {content_name} من قبل إدارة منصة سراج التعليمية"
    )
    
    