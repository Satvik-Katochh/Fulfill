"""
Serializers for the products app.
"""
from rest_framework import serializers
from .models import Product, ImportJob


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'description', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_sku(self, value):
        """Normalize SKU to lowercase."""
        return value.lower().strip() if value else value


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists."""
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ImportJobSerializer(serializers.ModelSerializer):
    """Serializer for ImportJob model."""
    
    class Meta:
        model = ImportJob
        fields = ['id', 'status', 'progress', 'total_records', 'processed_records', 
                  'error_message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'progress', 'total_records', 'processed_records', 
                           'error_message', 'created_at', 'updated_at']

