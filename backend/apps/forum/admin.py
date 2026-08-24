from django.contrib import admin

from .models import DiscussionComment, DiscussionTopic, ForumReport


@admin.register(DiscussionTopic)
class DiscussionTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'board', 'author', 'is_approved', 'is_locked', 'created_at')
    list_filter = ('kind', 'board', 'is_approved', 'is_locked')
    search_fields = ('title', 'content')


@admin.register(DiscussionComment)
class DiscussionCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'author', 'is_approved', 'is_expert', 'created_at')
    list_filter = ('is_approved', 'is_expert')


@admin.register(ForumReport)
class ForumReportAdmin(admin.ModelAdmin):
    list_display = ('reason', 'target_type', 'status', 'reporter', 'created_at')
    list_filter = ('reason', 'status', 'target_type')
    search_fields = ('details',)
