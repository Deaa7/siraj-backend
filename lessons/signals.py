# signals.py
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .models import Lessons
from .tasks import delete_video_from_cloud_and_db

@receiver(pre_save, sender=Lessons)
def trigger_video_cleanup(sender, instance, **kwargs):
    if not instance.pk:
        return # New lesson, nothing to clean up

    try:
        old_instance = Lessons.objects.get(pk=instance.pk)
        # LOGIC: If it WAS a video and is NOW changing to something else
        if old_instance.lesson_type == 'video' and instance.lesson_type != 'video':
            # Find the associated video record
 
                # Trigger the Celery task by ID
                delete_video_from_cloud_and_db.delay(old_instance.content_public_id)
         
                
    except Lessons.DoesNotExist:
        pass
    
@receiver(pre_delete, sender=Lessons)
def trigger_lesson_deletion(sender, instance, **kwargs):
    print('delete signal ' , instance)
    print('delete signal ' , instance.lesson_type)
    print('delete signal ' , instance.content_public_id)
    if instance.lesson_type == 'video':
        delete_video_from_cloud_and_db.delay(instance.content_public_id)
    else:
        pass
         