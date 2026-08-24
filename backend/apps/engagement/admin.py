from django.contrib import admin

from .models import Campaign, CampaignSignup, CivicEvent, CivicNews, EventSignup, Petition, Poll, SuspiciousContentReport


@admin.register(CivicNews)
class CivicNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'claim_type', 'status', 'published_at', 'organization')
    list_filter = ('topic', 'claim_type', 'status')
    search_fields = ('title', 'body', 'source_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CivicEvent)
class CivicEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'starts_at', 'status', 'organization')
    list_filter = ('kind', 'status')
    search_fields = ('title', 'description', 'location', 'source_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EventSignup)
class EventSignupAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'is_registered', 'reminder_enabled', 'organization')
    list_filter = ('is_registered', 'reminder_enabled')


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'kind', 'status', 'created_at', 'organization')
    list_filter = ('kind', 'status')
    search_fields = ('question', 'description')


admin.site.register(Petition)
admin.site.register(Campaign)
admin.site.register(CampaignSignup)
admin.site.register(SuspiciousContentReport)
