from django.contrib import admin
from .models import Comment
# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user_id','full_name','comment_text',"is_publisher" , 'created_at', 'exam_id', 'note_id', 'course_id', 'post_id', 'comment_id']
    
    def full_name(self, obj):
        name = ""
        if obj.user.account_category == "teacher":
            name = "الاستاذ " if obj.user.gender == "M" else "الآنسة " 
            name += obj.user.full_name
        elif obj.user.account_category == "team":
            name = "فريق " + obj.user.team_name
        else:
            name = obj.user.full_name
        name = name.strip()
        return name
    
    def is_publisher(self, obj):
        return obj.user.account_category == "teacher" or obj.user.account_category == "team"