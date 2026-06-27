from django.contrib import admin

from .models import TutorChat


@admin.register(TutorChat)
class TutorChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'session_id', 'tokens_used', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__email', 'message', 'session_id')
    readonly_fields = ('id', 'created_at')
