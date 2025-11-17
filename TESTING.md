# Testing Guide

## Setup Instructions

### 1. Activate Virtual Environment
```bash
source fulfill-assignment/bin/activate
```

### 2. Set Environment Variables
```bash
export USE_SQLITE=True  # Use SQLite for local testing
```

### 3. Run Migrations (if not done)
```bash
python manage.py migrate
```

### 4. Create Superuser (for Django Admin)
```bash
python manage.py createsuperuser
```

### 5. Start Django Server
```bash
python manage.py runserver
```

### 6. Start Celery Worker (in separate terminal)
```bash
# Make sure Redis is running first
redis-server

# Then start Celery
celery -A fulfill worker --loglevel=info
```

## Testing Checklist

### Backend API Testing

#### 1. Product CRUD
- [ ] Create product via POST `/api/products/`
- [ ] List products via GET `/api/products/`
- [ ] Filter by SKU, name, active status, description
- [ ] Update product via PUT `/api/products/{id}/`
- [ ] Delete product via DELETE `/api/products/{id}/`
- [ ] Test pagination

#### 2. CSV Upload
- [ ] Upload CSV via POST `/api/products/upload/`
- [ ] Check import job status via GET `/api/products/upload/{job_id}/status/`
- [ ] Verify progress updates
- [ ] Test with sample_products_500.csv
- [ ] Verify duplicate SKU handling (case-insensitive)

#### 3. Bulk Delete
- [ ] Delete all products via DELETE `/api/products/bulk-delete/`
- [ ] Verify confirmation required in UI

#### 4. Webhooks
- [ ] Create webhook via POST `/api/webhooks/`
- [ ] List webhooks via GET `/api/webhooks/`
- [ ] Update webhook via PUT `/api/webhooks/{id}/`
- [ ] Delete webhook via DELETE `/api/webhooks/{id}/`
- [ ] Test webhook via POST `/api/webhooks/{id}/test/`
- [ ] Verify webhooks trigger on product create/update/delete

### Frontend Testing

#### 1. Upload Page (`/upload/`)
- [ ] File upload works
- [ ] Progress bar updates in real-time
- [ ] Status messages display correctly
- [ ] Error handling works

#### 2. Products Page (`/products/`)
- [ ] Product list displays
- [ ] Filters work (SKU, name, active, description)
- [ ] Pagination works
- [ ] Create product modal works
- [ ] Edit product works
- [ ] Delete product works (with confirmation)
- [ ] Bulk delete works (with confirmation)

#### 3. Webhooks Page (`/webhooks/`)
- [ ] Webhook list displays
- [ ] Add webhook works
- [ ] Edit webhook works
- [ ] Delete webhook works
- [ ] Test webhook works

### Django Admin Testing
- [ ] Access admin at `/admin/`
- [ ] View products
- [ ] View import jobs
- [ ] View webhooks
- [ ] Edit products via admin

## Sample Test Data

Use `sample_products_500.csv` for testing CSV import functionality.

## Performance Testing

For large imports:
- Test with 500 rows (sample file)
- Test with full 500k rows (if time permits)
- Monitor progress updates
- Check database performance

## Known Issues to Check

1. Case-insensitive SKU matching
2. Duplicate overwrite behavior
3. Progress tracking accuracy
4. Webhook async execution
5. Error handling in all endpoints

