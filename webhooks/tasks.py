"""
Celery tasks for webhook operations.
"""
import requests
import logging
from typing import Dict, Any
from celery import shared_task
from .models import Webhook

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def trigger_webhook(self, webhook_id: int, event_type: str, data: Dict[str, Any]):
    """
    Trigger a webhook asynchronously.
    
    Args:
        webhook_id: ID of the webhook to trigger
        event_type: Type of event (product.created, product.updated, product.deleted)
        data: Data to send in the webhook payload
    
    Returns:
        Dict with webhook response details
    """
    try:
        webhook = Webhook.objects.get(id=webhook_id, enabled=True)
        
        if webhook.event_type != event_type:
            logger.warning(f"Webhook {webhook_id} event type mismatch")
            return {'status': 'skipped', 'reason': 'event_type_mismatch'}
        
        payload = {
            'event': event_type,
            'data': data,
            'timestamp': data.get('timestamp', ''),
        }
        
        # Send webhook request
        response = requests.post(
            webhook.url,
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status()
        
        logger.info(f"Webhook {webhook_id} triggered successfully: {response.status_code}")
        
        return {
            'status': 'success',
            'webhook_id': webhook_id,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None,
        }
        
    except Webhook.DoesNotExist:
        logger.warning(f"Webhook {webhook_id} not found or disabled")
        return {'status': 'skipped', 'reason': 'not_found_or_disabled'}
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook {webhook_id} failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
    except Exception as e:
        logger.error(f"Unexpected error triggering webhook {webhook_id}: {str(e)}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def trigger_webhooks_for_event(event_type: str, data: Dict[str, Any]):
    """
    Trigger all enabled webhooks for a specific event type.
    
    Args:
        event_type: Type of event (product.created, product.updated, product.deleted)
        data: Data to send in the webhook payload
    """
    webhooks = Webhook.objects.filter(event_type=event_type, enabled=True)
    
    for webhook in webhooks:
        trigger_webhook.delay(webhook.id, event_type, data)
    
    logger.info(f"Triggered {webhooks.count()} webhooks for event {event_type}")

