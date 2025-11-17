"""
Webhook models for the fulfill application.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator


class Webhook(models.Model):
    """
    Webhook model for configuring event notifications.

    Fields:
        - url: Webhook URL to send notifications to
        - event_type: Type of event to trigger webhook (product.created, product.updated, product.deleted)
        - enabled: Whether the webhook is enabled
        - created_at: Timestamp when webhook was created
        - updated_at: Timestamp when webhook was last updated
    """
    EVENT_TYPE_CHOICES = [
        ('product.created', 'Product Created'),
        ('product.updated', 'Product Updated'),
        ('product.deleted', 'Product Deleted'),
    ]

    url = models.URLField(max_length=500, validators=[
                          URLValidator()], help_text="Webhook URL")
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        help_text="Event type to trigger webhook"
    )
    enabled = models.BooleanField(
        default=True, db_index=True, help_text="Whether webhook is enabled")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'webhooks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['enabled']),
            models.Index(fields=['-created_at']),
        ]
        unique_together = [['url', 'event_type']]

    def __str__(self):
        return f"{self.event_type} -> {self.url}"
