"""
Serializers for the webhooks app.
"""
from rest_framework import serializers
from .models import Webhook


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for Webhook model."""
    
    class Meta:
        model = Webhook
        fields = ['id', 'url', 'event_type', 'enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_url(self, value):
        """Validate webhook URL."""
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        return value

