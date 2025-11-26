from django.db import models

from users.models import User
from courses.models import Course
from common.models import PublicModel

class CourseStatusTracking(PublicModel):
    
    course_id = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        related_name="course_status_tracking_course",
        null=True,
    )
    
 
    publisher_id = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="course_status_tracking_publisher",
        null=True,
    )
 
    student_id = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="course_status_tracking_student",
        null=True,
    )
   
    complete = models.BooleanField(default=False, blank=True)
    
    complete_date = models.DateTimeField(null=True, blank=True)
    # number_of_completed_lessons = models.IntegerField(
    #     default=0, blank=True, validators=[MinValueValidator(0)]
    # )

    class Meta:
        indexes = [
            models.Index(fields=[ 'student_id', '-created_at']),
            models.Index(fields=[ 'publisher_id', '-created_at']),
            models.Index(fields=[ 'course_id', '-created_at']),
        ]
