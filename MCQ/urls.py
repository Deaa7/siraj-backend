from django.urls import path
from .views import create_mcq, get_exam_mcqs, edit_mcq, delete_mcq,create_mcq_by_exam_public_id


urlpatterns = [
    path('create-mcq/', create_mcq, name='create_mcq'),
    path('create-mcq-by-exam-public-id/<str:exam_public_id>/', create_mcq_by_exam_public_id, name='create-mcq-by-exam-public-id'),
    path('get-exam-mcqs/', get_exam_mcqs, name='get_exam_mcqs'),
    path('edit-mcq/<str:mcq_public_id>/', edit_mcq, name='edit_mcq'),
    path('delete-mcq/<str:mcq_public_id>/', delete_mcq, name='delete_mcq'),
]