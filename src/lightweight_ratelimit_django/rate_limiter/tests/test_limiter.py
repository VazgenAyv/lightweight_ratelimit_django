from django.test import SimpleTestCase, RequestFactory
from django.core.cache import cache
from django.http import JsonResponse
from unittest.mock import patch

from lightweight_ratelimit_django.rate_limiter.limiter import RateLimiter 


def mock_view(request):
    return JsonResponse({"status": "OK"}, status=200)

class MockUser:
    """Mocks the User object with a primary key (pk) and minimal authentication attributes."""
    def __init__(self, pk, is_authenticated=True):
        self.pk = pk
        self.is_authenticated = is_authenticated

@patch('lightweight_ratelimit_django.rate_limiter.limiter.cache')
class RateLimiterTests(SimpleTestCase):
    
    def setUp(self):
        cache.clear() 
        self.factory = RequestFactory()

        self.user = MockUser(pk=420)
        self.anon_request = self.factory.get('/test/')
        self.user_request = self.factory.get('/test/')
        self.user_request.user = self.user
        self.anon_request.user = None
        
    def get_response(self, limit_args, request):
        """Helper to apply and call the decorator cleanly."""
        decorated_view = RateLimiter.view_rate_limit(**limit_args)(mock_view)
        return decorated_view(request)

    def test_view_rate_limit_anon_first_call(self, mock_cache):
        mock_cache.ttl.return_value = 3600
        mock_cache.get.side_effect = cache.get
        mock_cache.set.side_effect = cache.set
        response = self.get_response({}, self.anon_request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cache.get("RL:IP:127.0.0.1:/test/:H"), 49)

    def test_view_rate_limit_anon_block_call(self, mock_cache):
        mock_cache.ttl.return_value = 86400
        mock_cache.get.side_effect = cache.get
        mock_cache.set.side_effect = cache.set
        limits = {
            "limit": "2/d"
        }
        self.get_response(limits, self.anon_request)
        self.get_response(limits, self.anon_request)
        response = self.get_response(limits, self.anon_request)
        self.assertEqual(response.status_code, 429)

    def test_view_rate_limit_user_method_not_allowed(self, mock_cache):
        mock_cache.ttl.return_value = 60
        mock_cache.get.side_effect = cache.get
        mock_cache.set.side_effect = cache.set
        limits = {
            "methods": ["POST"],
            "limit": "1/m",
            "exclude_user": False
        }
        response = self.get_response(limits, self.user_request)
        self.assertEqual(response.status_code, 405)

    def test_view_rate_limit_user_method_pass(self, mock_cache):
        mock_cache.ttl.return_value = 60
        mock_cache.get.side_effect = cache.get
        mock_cache.set.side_effect = cache.set
        limits = {
            "methods": ["GET"],
            "limit": "2/m",
            "exclude_user": False
        }
        response = self.get_response(limits, self.user_request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cache.get("RL:USER:420:/test/:M"), 1)

    def test_view_rate_limit_wrong_limit(self, mock_cache):
        mock_cache.ttl.return_value = 60
        mock_cache.get.side_effect = cache.get
        mock_cache.set.side_effect = cache.set
        limits = {
            "methods": ["GET"],
            "limit": "2/s",
            "exclude_user": False
        }
        response = self.get_response(limits, self.user_request)
        self.assertEqual(response.status_code, 400)
