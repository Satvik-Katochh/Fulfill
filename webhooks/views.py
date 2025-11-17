"""
API views for webhooks app.
"""
import requests
import time
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Webhook
from .serializers import WebhookSerializer
from .tasks import trigger_webhook
import logging

logger = logging.getLogger(__name__)


class WebhookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Webhook CRUD operations.
    """
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer

    def get_queryset(self):
        """Filter webhooks by enabled status if requested."""
        queryset = Webhook.objects.all()
        enabled = self.request.query_params.get('enabled', None)
        if enabled is not None:
            queryset = queryset.filter(enabled=enabled.lower() == 'true')
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        Test a webhook by sending a sample payload.

        Returns:
            Response with status code, response time, and result
        """
        webhook = self.get_object()

        # Create sample payload
        sample_data = {
            'id': 999,
            'name': 'Test Product',
            'sku': 'test-sku',
            'description': 'This is a test webhook trigger',
            'active': True,
            'timestamp': timezone.now().isoformat(),
        }

        try:
            start_time = time.time()

            response = requests.post(
                webhook.url,
                json={
                    'event': webhook.event_type,
                    'data': sample_data,
                    'timestamp': sample_data['timestamp'],
                },
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )

            response_time = time.time() - start_time

            return Response({
                'status': 'success' if response.status_code < 400 else 'error',
                'status_code': response.status_code,
                'response_time': round(response_time, 3),
                # Limit response body length
                'response_body': response.text[:500],
            }, status=status.HTTP_200_OK)

        except requests.exceptions.Timeout:
            return Response({
                'status': 'error',
                'error': 'Request timeout',
                'response_time': None,
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            return Response({
                'status': 'error',
                'error': str(e),
                'response_time': None,
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(
                f"Unexpected error testing webhook {webhook.id}: {str(e)}")
            return Response({
                'status': 'error',
                'error': str(e),
                'response_time': None,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
