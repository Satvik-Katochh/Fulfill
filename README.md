# Product Importer - Fulfill Assignment

A scalable web application for importing and managing products from CSV files (up to 500,000 records).

## Features

- 📤 **CSV Import**: Upload and process large CSV files (500k+ records) with real-time progress tracking
- 📦 **Product Management**: Full CRUD operations with filtering and pagination
- 🗑️ **Bulk Operations**: Delete all products with confirmation
- 🔗 **Webhook System**: Configure and manage webhooks for product events
- ⚡ **Async Processing**: Celery-based background tasks for long-running operations

## Tech Stack

- **Framework**: Django 4.x
- **API**: Django REST Framework
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL
- **Frontend**: HTML/JavaScript (Simple, functional UI)

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver

# In separate terminal, run Celery worker
celery -A fulfill worker --loglevel=info
```

## Project Structure

```
fulfill/
├── fulfill/          # Main Django project
├── products/          # Products app
├── webhooks/          # Webhooks app
└── static/            # Frontend assets
```

## API Endpoints

### Products
- `GET /api/products/` - List products (with filters & pagination)
- `POST /api/products/` - Create product
- `GET /api/products/{id}/` - Get product
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product
- `POST /api/products/upload/` - Upload CSV file
- `GET /api/products/upload/{job_id}/status/` - Get upload progress
- `DELETE /api/products/bulk-delete/` - Delete all products

### Webhooks
- `GET /api/webhooks/` - List webhooks
- `POST /api/webhooks/` - Create webhook
- `PUT /api/webhooks/{id}/` - Update webhook
- `DELETE /api/webhooks/{id}/` - Delete webhook
- `POST /api/webhooks/{id}/test/` - Test webhook

## Development Notes

- CSV import processes in chunks for performance
- SKU is case-insensitive and unique
- Duplicate SKUs automatically overwrite existing records
- Progress tracking via polling or SSE
- Webhooks triggered asynchronously to avoid blocking

## Deployment

The application is designed to be deployed on platforms like:
- Render
- Heroku
- AWS
- GCP

See deployment documentation for platform-specific setup.

