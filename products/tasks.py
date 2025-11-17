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
        # First, count actual CSV records (not file lines, since CSV can have multi-line fields)
        total_records = 0
        skipped_count = 0
        skipped_reasons = []

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get('name', '').strip()
                sku = row.get('sku', '').strip().lower()
                if name and sku:
                    total_records += 1
                else:
                    skipped_count += 1
                    reason = f"Missing {'name' if not name else ''} {'SKU' if not sku else ''}".strip(
                    )
                    skipped_reasons.append(reason)

        logger.info(
            f"Total valid records: {total_records}, Skipped: {skipped_count}")
        if skipped_reasons:
            logger.warning(
                f"Skipped reasons: {dict((r, skipped_reasons.count(r)) for r in set(skipped_reasons))}")

        job.total_records = total_records
        job.save(update_fields=['total_records', 'updated_at'])

        # Process CSV in chunks
        chunk_size = 5000  # Process 5000 records at a time
        processed = 0
        created_count = 0
        updated_count = 0
        actual_skipped = 0

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            chunk = []

            # Start at 2 (after header)
            for row_num, row in enumerate(reader, start=2):
                # Normalize and validate row data
                name = row.get('name', '').strip()
                sku = row.get('sku', '').strip().lower()
                description = row.get('description', '').strip()

                if not name or not sku:
                    actual_skipped += 1
                    logger.warning(
                        f"Row {row_num}: Skipping - name='{name[:20]}...', sku='{sku[:20]}...'")
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
                    job.update_progress(processed, total_records)
                    logger.info(
                        f"Processed chunk: {processed}/{total_records} ({int(processed/total_records*100)}%)")
                    chunk = []

            # Process remaining records
            if chunk:
                created, updated = _process_chunk(chunk)
                created_count += created
                updated_count += updated
                processed += len(chunk)
                job.update_progress(processed, total_records)

        logger.info(
            f"Final: Processed={processed}, Created={created_count}, Updated={updated_count}, Skipped={actual_skipped}")

        # Mark job as completed
        job.status = 'completed'
        job.progress = 100
        job.save(update_fields=['status', 'progress', 'updated_at'])

        logger.info(
            f"Import completed: {created_count} created, {updated_count} updated, {actual_skipped} skipped")

        # Update job with final counts
        job.processed_records = processed
        job.save(update_fields=['processed_records', 'updated_at'])

        return {
            'status': 'completed',
            'created': created_count,
            'updated': updated_count,
            'total': processed,
            'skipped': actual_skipped
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
    Handles duplicates within chunk (last occurrence wins) and overwrites existing products.

    Args:
        chunk: List of product dictionaries

    Returns:
        Tuple of (created_count, updated_count)
    """
    created_count = 0
    updated_count = 0

    # First, handle duplicates within chunk (last occurrence wins)
    # Use dict to track last occurrence of each SKU in chunk
    chunk_by_sku = {}
    for item in chunk:
        sku_lower = item['sku'].lower()
        chunk_by_sku[sku_lower] = item  # Last occurrence overwrites previous ones

    # Get unique SKUs from deduplicated chunk
    unique_skus = list(chunk_by_sku.keys())

    # Fetch existing products by SKU (case-insensitive)
    existing_products = {
        p.sku.lower(): p for p in Product.objects.filter(sku__in=unique_skus)
    }

    products_to_create = []
    products_to_update = []

    # Process deduplicated chunk
    for sku_lower, item in chunk_by_sku.items():
        if sku_lower in existing_products:
            # Update existing product (overwrite)
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
