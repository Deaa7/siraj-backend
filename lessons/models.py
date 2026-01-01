from signal import signal
from django.db import models
from common.models import PublicModel
from courses.models import Course
from videos.models import Videos
from services.backblaze_bucket_manager import delete_video_from_bucket


class Lessons(PublicModel):
   
    TYPE_CHOICES = [
        ('video', 'Video'),
        ('exam', 'Exam'),
        ('note', 'Note'),
    ]
   
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
   
    lesson_type = models.CharField(max_length= 50, default='', choices=TYPE_CHOICES)
   
    content_public_id = models.CharField(max_length= 150, default='', blank=True, null=True)
    
    def delete(self, *args, **kwargs):
        # Run before deletion
        print(f"Deleting lesson {self.id}...")
        
        # Check if it's a video lesson
        if self.lesson_type == 'video' and self.content_public_id:
            # Find and delete the video
            video = Videos.objects.filter(public_id=self.content_public_id).first()
            print(f"Video: {video}")
            if video:
                delete_video_from_bucket(video.url)
                
                # Delete video record
                video.delete()
        
        # Now delete the lesson
        super().delete(*args, **kwargs)