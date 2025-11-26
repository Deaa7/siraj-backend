from django.db import models
from users.models import User
from exams.models import Exam
from notes.models import Note
from courses.models import Course
from posts.models import Post
from common.models import PublicModel
from django.core.validators import MinLengthValidator, MinValueValidator
# Create your models here.

class Comment(PublicModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_user')
    exam_id = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='comments_exam', null=True, blank=True)
    note_id = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comments_note', null=True, blank=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments_course', null=True, blank=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments_post', null=True, blank=True)
    comment_id = models.ForeignKey('self', on_delete=models.CASCADE, related_name='comments_comment', null=True, blank=True)
    comment_text = models.TextField(max_length=5000, default=''
                                    , validators=[MinLengthValidator(1)])
    number_of_replies = models.IntegerField(default=0, blank=True , validators=[MinValueValidator(0)])  
    
    class Meta:
        indexes = [
            models.Index(fields=['comment_id' , '-created_at']),
            models.Index(fields=['exam_id' , '-created_at']),
            models.Index(fields=['note_id' , '-created_at']),
            models.Index(fields=['course_id' , '-created_at']),
            models.Index(fields=['post_id' , '-created_at']),
        ]
        
        
        
        
        
