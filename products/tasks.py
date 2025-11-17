"""
Celery tasks for product operations.
"""
import csv
from typing import Dict, List, Tuple
from celery import shared_task
from django.db import connection
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
    Process a chunk of products using database-aware method.
    
    Automatically selects the best approach based on database type:
    - PostgreSQL: Uses UPSERT (atomic, faster)
    - SQLite: Uses query + bulk operations (compatible)
    
    Handles duplicates within chunk (last occurrence wins) and overwrites existing products.

    Args:
        chunk: List of product dictionaries

    Returns:
        Tuple of (created_count, updated_count)
    """
    # First, normalize and deduplicate chunk (last occurrence wins)
    chunk_by_sku = {}
    for item in chunk:
        # Ensure SKU is normalized to lowercase
        sku_lower = item['sku'].lower().strip()
        item['sku'] = sku_lower  # Normalize in place
        chunk_by_sku[sku_lower] = item  # Last occurrence overwrites previous ones

    # Detect database type and use appropriate method
    is_postgres = 'postgresql' in connection.vendor
    
    if is_postgres:
        # Use PostgreSQL UPSERT for atomic insert/update
        return _process_chunk_upsert(chunk_by_sku)
    else:
        # Use query-based method for SQLite compatibility
        return _process_chunk_query_based(chunk_by_sku)


def _process_chunk_upsert(chunk_by_sku: Dict[str, Dict]) -> Tuple[int, int]:
    """
    Process chunk using PostgreSQL UPSERT (ON CONFLICT).
    
    This method is faster and atomic - the database handles insert vs update.
    Only works with PostgreSQL.
    
    Args:
        chunk_by_sku: Dictionary mapping normalized SKU to product data
        
    Returns:
        Tuple of (created_count, updated_count)
    """
    if not chunk_by_sku:
        return 0, 0
    
    # Query existing products to get accurate counts
    unique_skus = list(chunk_by_sku.keys())
    existing_skus = set(
        Product.objects.filter(sku__in=unique_skus)
        .values_list('sku', flat=True)
    )
    
    # Count how many will be created vs updated
    created_count = sum(1 for sku in unique_skus if sku not in existing_skus)
    updated_count = len(existing_skus)
    
    # Build product list for UPSERT
    products = []
    for sku_lower, item in chunk_by_sku.items():
        products.append(Product(
            sku=sku_lower,
            name=item['name'],
            description=item['description'],
            active=item['active']
        ))
    
    try:
        # PostgreSQL UPSERT: database handles insert vs update atomically
        # update_conflicts=True uses ON CONFLICT DO UPDATE
        Product.objects.bulk_create(
            products,
            update_conflicts=True,
            unique_fields=['sku'],
            update_fields=['name', 'description', 'active', 'updated_at']
        )
        
        logger.debug(f"UPSERT processed {len(products)} products ({created_count} created, {updated_count} updated)")
        
        return created_count, updated_count
        
    except Exception as e:
        # Fallback to query-based method if UPSERT fails
        logger.warning(f"UPSERT failed, falling back to query-based method: {e}")
        return _process_chunk_query_based(chunk_by_sku)


def _process_chunk_query_based(chunk_by_sku: Dict[str, Dict]) -> Tuple[int, int]:
    """
    Process chunk using query + bulk operations (SQLite compatible).
    
    This method:
    1. Queries existing products by SKU
    2. Splits into create vs update lists
    3. Uses bulk_create with ignore_conflicts for safety
    4. Uses bulk_update for existing products
    
    Args:
        chunk_by_sku: Dictionary mapping normalized SKU to product data
        
    Returns:
        Tuple of (created_count, updated_count)
    """
    created_count = 0
    updated_count = 0

    # Get unique SKUs from deduplicated chunk
    unique_skus = list(chunk_by_sku.keys())

    # Fetch existing products by SKU
    existing_products = {}
    for product in Product.objects.filter(sku__in=unique_skus):
        existing_products[product.sku.lower()] = product

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
            # Create new product - ensure SKU is normalized
            # bulk_create bypasses save(), so normalize SKU manually
            product = Product(
                name=item['name'],
                sku=sku_lower,  # Already normalized
                description=item['description'],
                active=item['active']
            )
            products_to_create.append(product)

    # Bulk create new products
    # Use ignore_conflicts=True to handle race conditions where a product
    # might have been created between our query and this create operation
    if products_to_create:
        try:
            # Try bulk_create first for performance
            # ignore_conflicts=True will skip any that already exist (handles race conditions)
            created_objs = Product.objects.bulk_create(
                products_to_create, 
                ignore_conflicts=True
            )
            # Count actual created objects
            created_count = len(created_objs)
            
            # Handle any that were skipped due to conflicts
            # These are products that exist in DB but weren't in our initial query
            # (could be from a previous chunk or race condition)
            if len(created_objs) < len(products_to_create):
                # Find which SKUs were skipped
                created_skus = {obj.sku for obj in created_objs}
                skipped_products = [p for p in products_to_create if p.sku not in created_skus]
                
                # Update the skipped products (they already exist, so update them)
                if skipped_products:
                    skipped_skus = [p.sku for p in skipped_products]
                    existing_skipped = Product.objects.filter(sku__in=skipped_skus)
                    
                    for existing in existing_skipped:
                        matching_new = next((p for p in skipped_products if p.sku == existing.sku), None)
                        if matching_new:
                            existing.name = matching_new.name
                            existing.description = matching_new.description
                            existing.active = matching_new.active
                            products_to_update.append(existing)
                            updated_count += 1
                            
        except Exception as e:
            # Fallback: if bulk_create completely fails, use update_or_create
            logger.warning(f"bulk_create failed, falling back to update_or_create: {e}")
            created_count = 0
            for product in products_to_create:
                obj, was_created = Product.objects.update_or_create(
                    sku=product.sku,
                    defaults={
                        'name': product.name,
                        'description': product.description,
                        'active': product.active
                    }
                )
                if was_created:
                    created_count += 1
                else:
                    updated_count += 1

    # Bulk update existing products
    if products_to_update:
        Product.objects.bulk_update(
            products_to_update,
            fields=['name', 'description', 'active', 'updated_at']
        )

    return created_count, updated_count
