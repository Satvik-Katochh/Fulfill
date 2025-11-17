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
- Python 3.9+
- PostgreSQL (optional - SQLite works for development)
- Redis (for Celery task queue)

### Installation

```bash
# Activate virtual environment (already created as fulfill-assignment)
source fulfill-assignment/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Set environment variable for SQLite (for local testing)
export USE_SQLITE=True

# Run migrations
python manage.py migrate

# Create superuser (for Django admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver

# In separate terminal, start Redis (if not running)
redis-server

# In another terminal, run Celery worker
source fulfill-assignment/bin/activate
celery -A fulfill worker --loglevel=info
```

### Access the Application
- **Frontend**: http://localhost:8000/
- **Django Admin**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/products/

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

- CSV import processes in chunks (5000 records at a time) for optimal performance
- SKU is case-insensitive and unique (normalized to lowercase)
- Duplicate SKUs automatically overwrite existing records
- Progress tracking via polling (every 2 seconds)
- Webhooks triggered asynchronously via Celery to avoid blocking
- Sample CSV file (`sample_products_500.csv`) included for testing

## Testing

See [TESTING.md](TESTING.md) for comprehensive testing guide.

## Commit History

The project follows a clean commit history with logical phases:
- **Phase 1**: Backend foundation (Models, Admin, Migrations)
- **Phase 2**: Frontend UI (HTML/JS interface)
- **Phase 3**: Testing setup and fixes

## Deployment

The application is designed to be deployed on platforms like:
- Render
- Heroku
- AWS
- GCP

See deployment documentation for platform-specific setup.

