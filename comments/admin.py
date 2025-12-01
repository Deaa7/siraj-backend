from django.contrib import admin
from .models import Comment
# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user_id','full_name','comment_text',"is_publisher" , 'created_at', 'exam_id', 'note_id', 'course_id', 'post_id', 'comment_id']
    
    def full_name(self, obj):
        name = ""
        if obj.user_id.account_type == "teacher":
            name = "الاستاذ " if obj.user_id.gender == "M" else "الآنسة " 
            name += obj.user_id.full_name
        elif obj.user_id.account_type == "team":
            name = "فريق " + obj.user_id.team_name
        else:
            name = obj.user_id.full_name
        name = name.strip()
        return name
    
    def is_publisher(self, obj):
        return obj.user_id.account_type == "teacher" or obj.user_id.account_type == "team"