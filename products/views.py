"""
API views for products app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.utils import timezone
from .models import Product, ImportJob
from .serializers import ProductSerializer, ProductListSerializer, ImportJobSerializer
from .tasks import import_products_from_csv
from webhooks.tasks import trigger_webhooks_for_event
import logging

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        """Filter products based on query parameters."""
        queryset = Product.objects.all()

        # Filter by SKU
        sku = self.request.query_params.get('sku', None)
        if sku:
            queryset = queryset.filter(sku__icontains=sku.lower())

        # Filter by name
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Filter by active status
        active = self.request.query_params.get('active', None)
        if active is not None:
            queryset = queryset.filter(active=active.lower() == 'true')

        # Filter by description
        description = self.request.query_params.get('description', None)
        if description:
            queryset = queryset.filter(description__icontains=description)

        # Order by created_at descending (newest first) so newly created products appear on first page
        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Create a new product and trigger webhook."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Trigger webhook for product creation
        data = {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'description': product.description,
            'active': product.active,
            'timestamp': timezone.now().isoformat(),
        }
        trigger_webhooks_for_event.delay('product.created', data)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Update a product and trigger webhook."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Trigger webhook for product update
        data = {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'description': product.description,
            'active': product.active,
            'timestamp': timezone.now().isoformat(),
        }
        trigger_webhooks_for_event.delay('product.updated', data)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a product and trigger webhook."""
        instance = self.get_object()

        # Store product data before deletion for webhook
        data = {
            'id': instance.id,
            'name': instance.name,
            'sku': instance.sku,
            'description': instance.description,
            'active': instance.active,
            'timestamp': timezone.now().isoformat(),
        }

        instance.delete()

        # Trigger webhook for product deletion
        trigger_webhooks_for_event.delay('product.deleted', data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """
        Upload CSV file for product import.

        Returns:
            ImportJob ID and status
        """
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        csv_file = request.FILES['file']

        # Validate file extension
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV file'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Read CSV file content into memory
        csv_content = csv_file.read().decode('utf-8')

        # Create import job with file content stored in database
        # This allows the Celery worker (running on separate instance) to access the file
        import_job = ImportJob.objects.create(
            status='pending',
            progress=0,
            total_records=0,
            processed_records=0,
            file_content=csv_content
        )

        # Start async import task - pass job_id only, task will read from database
        import_products_from_csv.delay(import_job.id)

        serializer = ImportJobSerializer(import_job)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['get'], url_path='upload/(?P<job_id>[^/.]+)/status')
    def upload_status(self, request, job_id=None):
        """
        Get status of CSV import job.

        Args:
            job_id: ID of the import job

        Returns:
            ImportJob status and progress
        """
        try:
            import_job = ImportJob.objects.get(id=job_id)
            serializer = ImportJobSerializer(import_job)
            return Response(serializer.data)
        except ImportJob.DoesNotExist:
            return Response(
                {'error': 'Import job not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        Delete all products.

        Returns:
            Success message with count of deleted products
        """
        count = Product.objects.count()
        Product.objects.all().delete()

        # Trigger webhook for bulk deletion
        data = {
            'count': count,
            'timestamp': timezone.now().isoformat(),
        }
        trigger_webhooks_for_event.delay('product.deleted', data)

        return Response(
            {'message': f'Successfully deleted {count} products'},
            status=status.HTTP_200_OK
        )
