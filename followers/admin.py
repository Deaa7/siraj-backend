from django.contrib import admin

from .models import Followers


@admin.register(Followers)
class FollowersAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'followed', 'created_at')
    search_fields = (
        'follower_id__full_name',
        'follower_id__uuid',
        'followed_id__full_name',
        'followed_id__uuid',
    )
    autocomplete_fields = ('follower_id', 'followed_id')

    @staticmethod
    def follower(obj):
        return obj.follower_id

    @staticmethod
    def followed(obj):
        return obj.followed_id
