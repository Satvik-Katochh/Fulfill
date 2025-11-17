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

    def validate(self, attrs):
        """Validate that url and event_type combination is unique."""
        # Get the instance if this is an update
        instance = self.instance
        
        # For updates, use provided values or existing values from instance
        url = attrs.get('url', instance.url if instance else None)
        event_type = attrs.get('event_type', instance.event_type if instance else None)
        
        if url and event_type:
            # Check if another webhook with same url and event_type exists
            queryset = Webhook.objects.filter(url=url, event_type=event_type)
            
            # If updating, exclude the current instance
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'non_field_errors': ['A webhook with this URL and event type already exists.']
                })
        
        return attrs

