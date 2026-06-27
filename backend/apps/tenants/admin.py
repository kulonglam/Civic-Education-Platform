from django.contrib import admin

from .models import Membership, Organization, OrganizationInvite


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('is_active',)
    fields = ('name', 'slug', 'tagline', 'logo_url', 'primary_color', 'is_active')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('organization', 'user', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('organization__name', 'user__email')


@admin.register(OrganizationInvite)
class OrganizationInviteAdmin(admin.ModelAdmin):
    list_display = ('email', 'organization', 'role', 'expires_at', 'accepted_at', 'created_at')
    list_filter = ('role', 'accepted_at')
    search_fields = ('email', 'organization__name', 'token')
    readonly_fields = ('token', 'created_at', 'accepted_at')
