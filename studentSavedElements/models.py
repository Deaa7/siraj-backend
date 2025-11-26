from django.db import models
from users.models import User
from common.models import PublicModel
from exams.models import Exam
from notes.models import Note
from courses.models import Course
# Create your models here.

class StudentSavedElements(PublicModel):
    student_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_saved_elements')
    type = models.CharField(max_length= 50, default='')#exam, note, course
    exam_id = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_saved_elements_exam', null=True, blank=True)
    note_id = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='student_saved_elements_note', null=True, blank=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_saved_elements_course', null=True, blank=True)
    
        