# Implementation Plan - Product Importer

## 📊 CSV Format Analysis
- **Columns**: `name`, `sku`, `description`
- **Total Records**: ~861,688 rows
- **Key Requirements**: 
  - SKU is unique (case-insensitive)
  - Duplicates overwrite existing records
  - Products have `active` field (not in CSV, default True)

## 🏗️ Architecture Decisions

### Tech Stack
- **Framework**: Django 4.2+ (built-in ORM, admin, async support)
- **API**: Django REST Framework (clean, fast API development)
- **Task Queue**: Celery + Redis (async processing for large imports)
- **Database**: PostgreSQL (recommended, handles large datasets well)
- **Frontend**: Simple HTML/JS with Bootstrap (clean, functional UI)
- **Progress Tracking**: Polling (simpler than SSE/WebSockets, sufficient for this)

### Database Schema

#### Product Model
```python
- id (PK)
- name (CharField, indexed)
- sku (CharField, unique, case-insensitive, indexed)
- description (TextField)
- active (BooleanField, default=True, indexed)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

**Optimizations**:
- Index on `sku` (lowercase) for fast lookups
- Index on `name` for filtering
- Index on `active` for filtering
- Use `db_index=True` on frequently queried fields

#### Webhook Model
```python
- id (PK)
- url (URLField)
- event_type (CharField: 'product.created', 'product.updated', 'product.deleted')
- enabled (BooleanField, default=True)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

#### ImportJob Model (Progress Tracking)
```python
- id (PK)
- status (CharField: 'pending', 'processing', 'completed', 'failed')
- progress (IntegerField, 0-100)
- total_records (IntegerField)
- processed_records (IntegerField)
- error_message (TextField, nullable)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

## 🚀 Implementation Steps

### Phase 1: Project Setup
1. Initialize Django project
2. Create apps: `products`, `webhooks`
3. Configure settings (database, Celery, static files)
4. Set up requirements.txt

### Phase 2: Database Models
1. Create Product model with proper indexes
2. Create Webhook model
3. Create ImportJob model
4. Run migrations

### Phase 3: Celery Setup
1. Configure Celery with Redis
2. Create celery.py in project
3. Set up task routing

### Phase 4: CSV Import (Optimized)
1. **Upload Endpoint**: Accept CSV file, save to temp location
2. **Celery Task**: Process CSV in chunks (5000 records at a time)
3. **Chunked Processing Strategy**:
   - Read CSV in batches
   - For each batch:
     - Normalize SKU to lowercase for comparison
     - Use `bulk_update` for existing products
     - Use `bulk_create` for new products
   - Update progress after each chunk
4. **Duplicate Handling**: 
   - Query existing products by lowercase SKU
   - Update if exists, create if new
   - Use `get_or_create` or batch upsert pattern

### Phase 5: API Endpoints
1. **Products**:
   - `GET /api/products/` - List with filters, pagination
   - `POST /api/products/` - Create
   - `GET /api/products/{id}/` - Retrieve
   - `PUT /api/products/{id}/` - Update
   - `DELETE /api/products/{id}/` - Delete
   - `POST /api/products/upload/` - Upload CSV
   - `GET /api/products/upload/{job_id}/status/` - Get progress
   - `DELETE /api/products/bulk-delete/` - Delete all
2. **Webhooks**:
   - `GET /api/webhooks/` - List
   - `POST /api/webhooks/` - Create
   - `PUT /api/webhooks/{id}/` - Update
   - `DELETE /api/webhooks/{id}/` - Delete
   - `POST /api/webhooks/{id}/test/` - Test webhook

### Phase 6: Frontend UI
1. **Upload Page**:
   - File input with drag-drop
   - Progress bar with percentage
   - Status messages
   - Polling every 1-2 seconds for progress
2. **Products Page**:
   - Table with pagination
   - Filters (SKU, name, active, description)
   - Create/Edit modal
   - Delete with confirmation
   - Bulk delete button
3. **Webhooks Page**:
   - List of webhooks
   - Add/Edit form
   - Test button
   - Enable/Disable toggle

### Phase 7: Webhook System
1. **Trigger Points**: After product create/update/delete
2. **Async Execution**: Use Celery task to send webhook
3. **Error Handling**: Log failures, don't block main flow
4. **Test Endpoint**: Send sample payload, return response

### Phase 8: Optimizations
1. **Bulk Delete**: Use `Product.objects.all().delete()` (optimized by Django)
2. **Query Optimization**: Use `select_related`, `prefetch_related` where needed
3. **Pagination**: Limit to 50-100 items per page
4. **Caching**: Consider caching for frequently accessed data

## 📝 Code Quality Standards
- **Documentation**: Docstrings for all functions/classes
- **Type Hints**: Use Python type hints
- **Error Handling**: Comprehensive try-except blocks
- **Logging**: Use Python logging module
- **Validation**: Validate all inputs
- **Testing**: Unit tests for critical functions (if time permits)

## 🎯 Performance Targets
- **CSV Import**: Process 500k records in < 10 minutes
- **API Response**: < 200ms for list endpoints
- **Progress Updates**: Every 1-2 seconds
- **Bulk Delete**: < 5 seconds for 500k records

## 📦 File Structure
```
fulfill/
├── manage.py
├── requirements.txt
├── fulfill/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── celery.py
│   └── asgi.py
├── products/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── urls.py
│   └── admin.py
├── webhooks/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── tasks.py
│   └── urls.py
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── upload.html
│   ├── products.html
│   └── webhooks.html
└── uploads/  # Temporary CSV storage
```

