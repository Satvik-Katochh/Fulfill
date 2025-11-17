# Product Importer Assignment - Implementation Plan

## 📋 Requirements Summary

### Core Features Required:

1. **STORY 1: CSV File Upload (500k records)**
   - Upload large CSV via UI
   - Real-time progress indicator
   - Auto-overwrite duplicates by SKU (case-insensitive)
   - SKU must be unique
   - Products can be active/inactive
   - Optimized for large files

2. **STORY 1A: Upload Progress Visibility**
   - Real-time progress updates
   - Visual progress bar/percentage
   - Status messages (Parsing, Validating, Import Complete)
   - Error handling with retry option
   - Use SSE/WebSockets/Polling

3. **STORY 2: Product Management UI**
   - CRUD operations (Create, Read, Update, Delete)
   - Filter by SKU, name, active status, description
   - Pagination
   - Inline editing or modal forms
   - Delete confirmation

4. **STORY 3: Bulk Delete**
   - Delete all products from UI
   - Confirmation dialog
   - Success/failure notifications

5. **STORY 4: Webhook Configuration**
   - Add, edit, test, delete webhooks
   - Display URLs, event types, enable/disable status
   - Test trigger with response code/time
   - Non-blocking processing

### Tech Stack Requirements:

- **Framework**: Django (chosen for built-in features)
- **Async Tasks**: Celery with Redis
- **Database**: PostgreSQL
- **ORM**: Django ORM (built-in)
- **Deployment**: Render/Heroku/AWS (free tier)

## 🏗️ Architecture Plan

### Backend-First Approach (Recommended)

1. **Phase 1: Backend Core** (Priority)
   - Django project setup
   - Database models (Product, Webhook)
   - REST API endpoints (Django REST Framework)
   - Celery task for CSV import
   - Progress tracking mechanism

2. **Phase 2: Frontend** (Can be simple)
   - Basic HTML/JS frontend
   - Or use Django templates
   - Progress polling/SSE implementation

### Project Structure:

```
fulfill/
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
├── fulfill/              # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/             # Products app
│   ├── models.py        # Product model
│   ├── views.py         # API views
│   ├── serializers.py   # DRF serializers
│   ├── tasks.py         # Celery tasks
│   └── urls.py
├── webhooks/            # Webhooks app
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
└── static/              # Frontend assets
    └── js/
```

## 🎯 Implementation Strategy

### Database Models:

1. **Product**
   - sku (unique, case-insensitive)
   - name
   - description
   - active (boolean)
   - created_at, updated_at

2. **Webhook**
   - url
   - event_type (choices: product.created, product.updated, product.deleted)
   - enabled (boolean)
   - created_at, updated_at

3. **ImportJob** (for tracking progress)
   - status (pending, processing, completed, failed)
   - progress (0-100)
   - total_records
   - processed_records
   - error_message
   - created_at, updated_at

### API Endpoints Needed:

- `POST /api/products/upload/` - Upload CSV
- `GET /api/products/upload/{job_id}/status/` - Get upload progress
- `GET /api/products/` - List products (with filters, pagination)
- `POST /api/products/` - Create product
- `GET /api/products/{id}/` - Get product
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product
- `DELETE /api/products/bulk-delete/` - Delete all products
- `GET /api/webhooks/` - List webhooks
- `POST /api/webhooks/` - Create webhook
- `PUT /api/webhooks/{id}/` - Update webhook
- `DELETE /api/webhooks/{id}/` - Delete webhook
- `POST /api/webhooks/{id}/test/` - Test webhook

### Celery Tasks:

- `import_products_from_csv(file_path, job_id)` - Process CSV in chunks
- `trigger_webhook(webhook_id, event_type, data)` - Async webhook calls

## ⏱️ Time Assessment

### Is 24 hours realistic? **YES, but tight**

**Breakdown:**

- **Backend Setup**: 2-3 hours
  - Django project, models, migrations
  - Celery + Redis setup
  - Basic API structure

- **CSV Import Feature**: 4-5 hours
  - File upload endpoint
  - Celery task for processing
  - Progress tracking
  - Duplicate handling (case-insensitive SKU)

- **Product CRUD API**: 2-3 hours
  - List, create, update, delete
  - Filtering, pagination

- **Bulk Delete**: 1 hour

- **Webhook System**: 3-4 hours
  - Webhook model & CRUD
  - Event triggers
  - Async webhook calls

- **Frontend (Simple)**: 3-4 hours
  - Basic HTML/JS
  - Progress polling
  - Forms for CRUD

- **Testing & Bug Fixes**: 2-3 hours

- **Deployment**: 2-3 hours
  - Setup on Render/Heroku
  - Environment variables
  - Database setup

**Total: ~20-26 hours** (with focused work)

### Tips for Success:

1. ✅ **Start with backend** - Get API working first
2. ✅ **Use Django REST Framework** - Faster API development
3. ✅ **Simple frontend** - Basic HTML/JS is acceptable
4. ✅ **Test incrementally** - Don't wait until the end
5. ✅ **Commit frequently** - Show your process
6. ✅ **Document as you go** - Comments and README

## 🚀 Next Steps

1. Initialize Django project
2. Set up PostgreSQL database
3. Create models and migrations
4. Set up Celery + Redis
5. Build CSV import task
6. Create REST API endpoints
7. Build simple frontend
8. Deploy to Render/Heroku

## 📝 Notes

- Django is a good choice because:
  - Built-in ORM (no SQLAlchemy needed)
  - Admin interface for quick testing
  - Good Celery integration
  - Can use DRF for clean APIs
- For 500k records:
  - Process in chunks (1000-5000 records at a time)
  - Use bulk_create/update for performance
  - Track progress in database
- Progress tracking:
  - Use polling (simpler) or SSE (better UX)
  - Store progress in ImportJob model
  - Update from Celery task
