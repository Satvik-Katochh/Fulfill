"""
Django admin configuration for webhooks app.
"""
from django.contrib import admin
from .models import Webhook


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """Admin interface for Webhook model."""
    list_display = ['id', 'url', 'event_type', 'enabled', 'created_at', 'updated_at']
    list_filter = ['event_type', 'enabled', 'created_at']
    search_fields = ['url']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['enabled']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Webhook Configuration', {
            'fields': ('url', 'event_type', 'enabled')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
