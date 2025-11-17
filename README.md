# Product Importer - Fulfill Assignment

A scalable Django web application for importing and managing products from CSV files (up to 500,000 records) with real-time progress tracking, webhook support, and full CRUD operations.

## 🚀 Live Deployment

**Application URL:** [http://3.235.20.127](http://3.235.20.127)

The application is deployed on AWS EC2 and is fully functional. All features are working and ready for review.

---

## ✅ Requirements Implementation

This application implements all requirements from the screening task:

### ✅ STORY 1 — File Upload via UI
- ✅ Upload large CSV files (up to 500,000 products) through web interface
- ✅ Clear and intuitive file upload component
- ✅ Real-time progress indicator (percentage and progress bar)
- ✅ Automatic overwrite of duplicates based on SKU (case-insensitive)
- ✅ SKU uniqueness enforced across all records
- ✅ Products can be marked as active/inactive
- ✅ Optimized for large files with chunked processing

### ✅ STORY 1A — Upload Progress Visibility
- ✅ Real-time progress updates (polling every 2 seconds)
- ✅ Visual progress bar and percentage display
- ✅ Status messages ("Processing", "Completed", "Failed")
- ✅ Error messages with failure reasons
- ✅ Smooth, interactive visual experience

### ✅ STORY 2 — Product Management UI
- ✅ View, create, update, and delete products from web interface
- ✅ Filtering by SKU, name, active status, and description
- ✅ Paginated product list (50 products per page)
- ✅ Modal form for creating/updating products
- ✅ Deletion with confirmation dialog
- ✅ Clean, minimalist design

### ✅ STORY 3 — Bulk Delete from UI
- ✅ Delete all products with one click
- ✅ Confirmation dialog ("Are you sure? This cannot be undone.")
- ✅ Success/failure notifications
- ✅ Visual feedback during processing

### ✅ STORY 4 — Webhook Configuration via UI
- ✅ Add, edit, test, and delete webhooks from UI
- ✅ Display webhook URLs, event types, and enable/disable status
- ✅ Visual confirmation of test triggers (response code, response time)
- ✅ Asynchronous webhook processing (non-blocking)

---

## 🎯 How to Use the Application

### 1. Upload CSV File (STORY 1 & 1A)

1. **Navigate to Upload Page:**
   - Go to: [http://3.235.20.127/upload/](http://3.235.20.127/upload/)
   - Or click "Upload CSV" from the homepage

2. **Upload Your CSV File:**
   - Click "Choose File" or drag and drop your CSV file
   - CSV format: `name,sku,description` (header required)
   - Click "Upload and Import"

3. **Monitor Progress:**
   - Real-time progress bar shows percentage complete
   - Status updates: "Pending" → "Processing" → "Completed"
   - Progress updates every 2 seconds automatically
   - If error occurs, error message is displayed

4. **View Results:**
   - After completion, click "View Products" to see imported products
   - Products are automatically deduplicated by SKU (case-insensitive)
   - Duplicate SKUs overwrite existing records

**Sample CSV Format:**
```csv
name,sku,description
Product Name,ABC-123,Product description here
Another Product,XYZ-456,Another description
```

**Test with Sample File:**
- Use `sample_products_500.csv` included in the repository (500 products)
- Or use the full 500,000 product CSV from the Google Drive link in requirements

---

### 2. Manage Products (STORY 2)

1. **View Products:**
   - Go to: [http://3.235.20.127/products/](http://3.235.20.127/products/)
   - Products are displayed in a paginated table (50 per page)
   - Use "Previous" and "Next" buttons to navigate

2. **Filter Products:**
   - Use filter inputs at the top:
     - **SKU**: Filter by SKU (case-insensitive)
     - **Name**: Filter by product name
     - **Active**: Filter by active status (All/Active/Inactive)
     - **Description**: Filter by description text
   - Click "Apply Filters" or press Enter
   - Click "Clear Filters" to reset

3. **Create Product:**
   - Click "Create Product" button
   - Fill in the form:
     - **Name**: Product name (required)
     - **SKU**: Unique SKU (required, case-insensitive)
     - **Description**: Product description (optional)
     - **Active**: Checkbox to mark as active/inactive
   - Click "Save Product"
   - Success notification appears

4. **Edit Product:**
   - Click the blue "Edit" button (pencil icon) next to any product
   - Modify the fields in the modal
   - Click "Save Product"
   - Product is updated immediately

5. **Delete Product:**
   - Click the red "Delete" button (trash icon) next to any product
   - Confirm deletion in the dialog
   - Product is removed and list refreshes automatically

---

### 3. Bulk Delete (STORY 3)

1. **Delete All Products:**
   - Go to Products page: [http://3.235.20.127/products/](http://3.235.20.127/products/)
   - Click "Delete All Products" button (red button at top)
   - Confirm in the dialog: "Are you sure? This cannot be undone!"
   - Click "OK" to proceed
   - All products are deleted
   - Success notification appears
   - List refreshes to show empty state

**⚠️ Warning:** This action cannot be undone. Use with caution.

---

### 4. Configure Webhooks (STORY 4)

1. **Access Webhooks Page:**
   - Go to: [http://3.235.20.127/webhooks/](http://3.235.20.127/webhooks/)

2. **Create Webhook:**
   - Click "Create Webhook" button
   - Fill in the form:
     - **URL**: Your webhook endpoint URL (e.g., `https://your-server.com/webhook`)
     - **Event Type**: Select from dropdown:
       - `product.created` - Triggered when product is created
       - `product.updated` - Triggered when product is updated
       - `product.deleted` - Triggered when product is deleted
     - **Enabled**: Checkbox to enable/disable webhook
   - Click "Save Webhook"
   - Webhook appears in the list

3. **Test Webhook:**
   - Click "Test" button (green button) next to any webhook
   - System sends a test payload to your webhook URL
   - Results show:
     - **Status Code**: HTTP response code (200, 404, etc.)
     - **Response Time**: Time taken in milliseconds
     - **Status**: Success or Error
   - If webhook URL is invalid, error is displayed

4. **Edit Webhook:**
   - Click "Edit" button (blue pencil icon) next to any webhook
   - Modify URL, event type, or enabled status
   - Click "Save Webhook"

5. **Disable/Enable Webhook:**
   - Edit the webhook and uncheck/check "Enabled"
   - Disabled webhooks won't trigger on events
   - Enabled webhooks trigger automatically on matching events

6. **Delete Webhook:**
   - Click "Delete" button (red trash icon)
   - Confirm deletion
   - Webhook is removed

**Webhook Payload Example:**
```json
{
  "id": 123,
  "name": "Product Name",
  "sku": "abc-123",
  "description": "Product description",
  "active": true,
  "timestamp": "2025-11-17T10:30:00Z"
}
```

**Webhook Events:**
- `product.created`: Triggered when a product is created (via UI or CSV import)
- `product.updated`: Triggered when a product is updated
- `product.deleted`: Triggered when a product is deleted (single or bulk)

**Testing Your Webhook Endpoint:**
You can use services like:
- [webhook.site](https://webhook.site) - Get a temporary webhook URL for testing
- [httpbin.org](https://httpbin.org/post) - Test POST requests
- Your own server endpoint

---

## 🛠️ Tech Stack

- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Task Queue**: Celery 5.3.4 + Redis 5.0.1
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: HTML5, JavaScript, Bootstrap 5
- **Server**: Gunicorn + Nginx
- **Deployment**: AWS EC2

---

## 📋 API Endpoints

### Products API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/products/` | List products (with filters & pagination) |
| `POST` | `/api/products/` | Create product |
| `GET` | `/api/products/{id}/` | Get product details |
| `PUT` | `/api/products/{id}/` | Update product |
| `DELETE` | `/api/products/{id}/` | Delete product |
| `POST` | `/api/products/upload/` | Upload CSV file |
| `GET` | `/api/products/upload/{job_id}/status/` | Get upload progress |
| `DELETE` | `/api/products/bulk-delete/` | Delete all products |

### Webhooks API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/webhooks/` | List webhooks |
| `POST` | `/api/webhooks/` | Create webhook |
| `GET` | `/api/webhooks/{id}/` | Get webhook details |
| `PUT` | `/api/webhooks/{id}/` | Update webhook |
| `DELETE` | `/api/webhooks/{id}/` | Delete webhook |
| `POST` | `/api/webhooks/{id}/test/` | Test webhook |

**API Base URL:** `http://3.235.20.127/api/`

---

## 🔧 Key Features & Implementation Details

### CSV Import
- **Chunked Processing**: Processes 5,000 records at a time for optimal performance
- **SKU Normalization**: All SKUs are normalized to lowercase for case-insensitive matching
- **Duplicate Handling**: Last occurrence of duplicate SKU overwrites previous ones
- **Progress Tracking**: Real-time progress via polling (updates every 2 seconds)
- **Error Handling**: Comprehensive error messages with retry capability

### Product Management
- **Pagination**: 50 products per page
- **Filtering**: Multiple filter options with real-time application
- **Validation**: Client-side and server-side validation
- **Responsive Design**: Works on desktop and mobile devices

### Webhooks
- **Asynchronous Processing**: Webhooks triggered via Celery (non-blocking)
- **Event Types**: Supports product.created, product.updated, product.deleted
- **Error Handling**: Failed webhooks don't block main operations
- **Testing**: Built-in test functionality with response details

### Performance Optimizations
- **Bulk Operations**: Uses `bulk_create` and `bulk_update` for efficient database operations
- **Async Tasks**: Long-running operations handled by Celery workers
- **Database Indexing**: SKU field indexed for fast lookups
- **Chunked Processing**: Large files processed in manageable chunks

---

## 🧪 Testing Guide

### Quick Test Scenario

1. **Upload CSV:**
   - Upload `sample_products_500.csv` (included in repo)
   - Watch progress bar update in real-time
   - Verify products appear in list

2. **Create Product:**
   - Create a new product via UI
   - Verify it appears in the list

3. **Filter Products:**
   - Use filters to search for products
   - Verify results update correctly

4. **Edit Product:**
   - Edit an existing product
   - Verify changes are saved

5. **Delete Product:**
   - Delete a single product
   - Verify it's removed from list

6. **Bulk Delete:**
   - Delete all products
   - Verify list is empty

7. **Webhook Test:**
   - Create a webhook pointing to [webhook.site](https://webhook.site)
   - Create/update/delete a product
   - Check webhook.site to see the payload received

### Test with Large File

1. Download the 500,000 product CSV from the Google Drive link in requirements
2. Upload via the UI
3. Monitor progress (may take several minutes)
4. Verify all products are imported correctly

---

## 📁 Project Structure

```
Fulfill/
├── fulfill/              # Main Django project
│   ├── settings.py      # Configuration
│   ├── urls.py          # URL routing
│   └── celery.py        # Celery configuration
├── products/             # Products app
│   ├── models.py        # Product and ImportJob models
│   ├── views.py         # API views
│   ├── tasks.py         # Celery tasks (CSV import)
│   └── migrations/      # Database migrations
├── webhooks/             # Webhooks app
│   ├── models.py        # Webhook model
│   ├── views.py         # API views
│   └── tasks.py         # Celery tasks (webhook triggers)
├── templates/            # HTML templates
│   ├── index.html       # Homepage
│   ├── upload.html      # CSV upload page
│   ├── products.html    # Product management page
│   └── webhooks.html    # Webhook management page
├── static/               # Static files (CSS, JS)
├── requirements.txt     # Python dependencies
└── manage.py            # Django management script
```

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.9+
- PostgreSQL (optional - SQLite works for development)
- Redis (for Celery)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Fulfill

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (for SQLite development)
export USE_POSTGRES=False  # Uses SQLite by default

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Start Redis (in separate terminal)
redis-server

# Start Celery worker (in separate terminal)
celery -A fulfill worker --loglevel=info

# Start development server
python manage.py runserver
```

### Access Application
- **Frontend**: http://localhost:8000/
- **API**: http://localhost:8000/api/products/
- **Django Admin**: http://localhost:8000/admin/

---

## 📝 Code Quality

- **Clean Code**: Well-documented, readable, and maintainable
- **Standards Compliant**: Follows Django and Python best practices
- **Error Handling**: Comprehensive error handling throughout
- **Type Hints**: Type annotations where appropriate
- **Comments**: Clear comments explaining complex logic

---

## 📊 Commit History

The project follows a clean, logical commit history:
- **Initial Setup**: Project structure, models, migrations
- **Backend Development**: API endpoints, Celery tasks, business logic
- **Frontend Development**: UI components, JavaScript functionality
- **Testing & Fixes**: Bug fixes, edge cases, optimizations
- **Deployment**: Production configuration, service setup

Each commit is focused and meaningful, demonstrating clear planning and execution.

---

## 🌐 Deployment

The application is deployed on **AWS EC2** with:
- **Gunicorn**: Production WSGI server
- **Nginx**: Reverse proxy and static file serving
- **PostgreSQL**: Production database
- **Redis**: Celery message broker
- **Systemd**: Service management for Gunicorn and Celery

**Deployment URL:** [http://3.235.20.127](http://3.235.20.127)

---

## 📧 Contact & Support

For questions or issues, please refer to the commit history and code comments for implementation details.

---

## ✅ Assignment Checklist

- ✅ All 5 stories implemented and working
- ✅ Clean, readable code with good documentation
- ✅ Meaningful commit history
- ✅ Deployed on public platform (AWS EC2)
- ✅ Handles long-running operations (Celery async tasks)
- ✅ Real-time progress tracking
- ✅ Webhook system fully functional
- ✅ All CRUD operations working
- ✅ Error handling and user feedback
- ✅ Optimized for large datasets (500k+ records)

---

**Last Updated:** November 17, 2025
