"""
Product models for the fulfill application.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator


class Product(models.Model):
    """
    Product model representing items imported from CSV.

    Fields:
        - name: Product name
        - sku: Stock Keeping Unit (unique, case-insensitive)
        - description: Product description
        - active: Whether the product is active (default: True)
        - created_at: Timestamp when product was created
        - updated_at: Timestamp when product was last updated
    """
    name = models.CharField(
        max_length=255, db_index=True, help_text="Product name")
    sku = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        validators=[MinLengthValidator(1)],
        help_text="Stock Keeping Unit (case-insensitive, unique)"
    )
    description = models.TextField(
        blank=True, null=True, help_text="Product description")
    active = models.BooleanField(
        default=True, db_index=True, help_text="Whether the product is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        """Override save to normalize SKU to lowercase for case-insensitive uniqueness."""
        self.sku = self.sku.lower().strip()
        super().save(*args, **kwargs)


class ImportJob(models.Model):
    """
    Model to track CSV import progress.

    Fields:
        - status: Current status of the import (pending, processing, completed, failed)
        - progress: Progress percentage (0-100)
        - total_records: Total number of records to process
        - processed_records: Number of records processed so far
        - error_message: Error message if import failed
        - file_content: CSV file content stored in database (for worker access on Render)
        - created_at: Timestamp when import job was created
        - updated_at: Timestamp when import job was last updated
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    progress = models.IntegerField(
        default=0, help_text="Progress percentage (0-100)")
    total_records = models.IntegerField(
        default=0, help_text="Total number of records")
    processed_records = models.IntegerField(
        default=0, help_text="Number of records processed")
    error_message = models.TextField(
        blank=True, null=True, help_text="Error message if failed")
    file_content = models.TextField(
        blank=True, null=True, help_text="CSV file content stored in database for worker access")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'import_jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"ImportJob {self.id} - {self.status} ({self.progress}%)"

    def update_progress(self, processed: int, total: int):
        """Update progress based on processed and total records."""
        self.processed_records = processed
        self.total_records = total
        if total > 0:
            self.progress = int((processed / total) * 100)
        else:
            self.progress = 0
        self.save(update_fields=['processed_records',
                  'total_records', 'progress', 'updated_at'])
