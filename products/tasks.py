"""
Celery tasks for product operations.
"""
import csv
import os
from typing import Dict, List, Tuple
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from .models import Product, ImportJob
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def import_products_from_csv(self, file_path: str, job_id: int):
    """
    Import products from CSV file in chunks for optimal performance.
    
    Args:
        file_path: Path to the CSV file
        job_id: ID of the ImportJob tracking this import
    
    Returns:
        Dict with import results
    """
    job = ImportJob.objects.get(id=job_id)
    job.status = 'processing'
    job.save(update_fields=['status', 'updated_at'])
    
    try:
        # Count total lines first (excluding header)
        total_lines = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f) - 1  # Subtract header
        
        job.total_records = total_lines
        job.save(update_fields=['total_records', 'updated_at'])
        
        # Process CSV in chunks
        chunk_size = 5000  # Process 5000 records at a time
        processed = 0
        created_count = 0
        updated_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            chunk = []
            
            for row in reader:
                # Normalize and validate row data
                name = row.get('name', '').strip()
                sku = row.get('sku', '').strip().lower()
                description = row.get('description', '').strip()
                
                if not name or not sku:
                    logger.warning(f"Skipping row with missing name or SKU: {row}")
                    continue
                
                chunk.append({
                    'name': name,
                    'sku': sku,
                    'description': description,
                    'active': True,  # Default to active
                })
                
                # Process chunk when it reaches chunk_size
                if len(chunk) >= chunk_size:
                    created, updated = _process_chunk(chunk)
                    created_count += created
                    updated_count += updated
                    processed += len(chunk)
                    
                    # Update progress
                    job.update_progress(processed, total_lines)
                    chunk = []
            
            # Process remaining records
            if chunk:
                created, updated = _process_chunk(chunk)
                created_count += created
                updated_count += updated
                processed += len(chunk)
                job.update_progress(processed, total_lines)
        
        # Mark job as completed
        job.status = 'completed'
        job.progress = 100
        job.save(update_fields=['status', 'progress', 'updated_at'])
        
        logger.info(f"Import completed: {created_count} created, {updated_count} updated")
        
        return {
            'status': 'completed',
            'created': created_count,
            'updated': updated_count,
            'total': processed
        }
        
    except Exception as e:
        logger.error(f"Import failed: {str(e)}", exc_info=True)
        job.status = 'failed'
        job.error_message = str(e)
        job.save(update_fields=['status', 'error_message', 'updated_at'])
        raise


def _process_chunk(chunk: List[Dict]) -> Tuple[int, int]:
    """
    Process a chunk of products using bulk operations.
    
    Args:
        chunk: List of product dictionaries
    
    Returns:
        Tuple of (created_count, updated_count)
    """
    created_count = 0
    updated_count = 0
    
    # Get all SKUs from chunk (normalized to lowercase)
    skus = [item['sku'].lower() for item in chunk]
    
    # Fetch existing products by SKU (case-insensitive)
    existing_products = {
        p.sku.lower(): p for p in Product.objects.filter(sku__in=skus)
    }
    
    products_to_create = []
    products_to_update = []
    
    for item in chunk:
        sku_lower = item['sku'].lower()
        
        if sku_lower in existing_products:
            # Update existing product
            product = existing_products[sku_lower]
            product.name = item['name']
            product.description = item['description']
            product.active = item['active']
            products_to_update.append(product)
            updated_count += 1
        else:
            # Create new product
            products_to_create.append(Product(**item))
            created_count += 1
    
    # Bulk create new products
    if products_to_create:
        Product.objects.bulk_create(products_to_create, ignore_conflicts=False)
    
    # Bulk update existing products
    if products_to_update:
        Product.objects.bulk_update(
            products_to_update,
            fields=['name', 'description', 'active', 'updated_at']
        )
    
    return created_count, updated_count

