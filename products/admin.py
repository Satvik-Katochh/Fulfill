"""
Django admin configuration for products app.
"""
from django.contrib import admin
from .models import Product, ImportJob


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""
    list_display = ['id', 'name', 'sku', 'active', 'created_at', 'updated_at']
    list_filter = ['active', 'created_at', 'updated_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'sku', 'description', 'active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    """Admin interface for ImportJob model."""
    list_display = ['id', 'status', 'progress', 'processed_records', 'total_records', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['status', 'progress', 'processed_records', 'total_records', 
                      'error_message', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Job Status', {
            'fields': ('status', 'progress', 'processed_records', 'total_records')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable manual creation of import jobs."""
        return False
