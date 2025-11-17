"""
Custom middleware to exempt API routes from CSRF protection.
"""
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt


class DisableCSRFForAPI(MiddlewareMixin):
    """
    Middleware to disable CSRF protection for API endpoints.
    This is safe because API endpoints use DRF authentication, not session-based auth.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Exempt all /api/ routes from CSRF
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
