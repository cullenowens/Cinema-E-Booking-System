from django.utils.deprecation import MiddlewareMixin

class DisableCSRFForAdminAPI(MiddlewareMixin):
    """Disable CSRF for admin API endpoints since they use JWT authentication"""
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            setattr(request, '_dont_enforce_csrf_checks', True)