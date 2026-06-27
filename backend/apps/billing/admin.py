from django.contrib import admin

from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price_cents', 'currency', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('organization', 'plan', 'status', 'current_period_end')
    list_filter = ('status', 'plan')
    search_fields = ('organization__name',)
