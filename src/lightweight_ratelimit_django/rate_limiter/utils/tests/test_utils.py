from django.test import SimpleTestCase, RequestFactory
from django.core.cache import cache

from lightweight_ratelimit_django.rate_limiter.utils.utils import (
    get_requester_ip,
    seconds_to_readable,
) 


class MockUser:
    """Mocks the User object with a primary key (pk) and minimal authentication attributes."""
    def __init__(self, pk, is_authenticated=True):
        self.pk = pk
        self.is_authenticated = is_authenticated

class RateLimiterTests(SimpleTestCase):
    
    def setUp(self):
        cache.clear() 
        self.factory = RequestFactory()
        
        self.user = MockUser(pk=420)
        self.anon_request = self.factory.get('/test/')
        self.user_request = self.factory.get('/test/')
        self.user_request.user = self.user

    def test_get_requester_ip_forwarded(self):
        self.anon_request.META["HTTP_X_FORWARDED_FOR"] = '9.9.9.9,10.10.10.10'
        result = get_requester_ip(self.anon_request)
        self.assertEqual(result, "9.9.9.9")

    def test_get_requester_ip_no_forwarded(self):
        self.anon_request.META["REMOTE_ADDR"] = '9.9.9.9'
        result = get_requester_ip(self.anon_request)
        self.assertEqual(result, "9.9.9.9")

    def test_get_requester_ip_no_remote(self):
        self.anon_request.META["REMOTE_ADDR"] = None
        result = get_requester_ip(self.anon_request)
        self.assertEqual(result, "0.0.0.0")

    def test_seconds_to_readable(self):

        # one second
        result = seconds_to_readable(1)
        self.assertEqual(result, "1 second")

        # only seconds
        result = seconds_to_readable(10)
        self.assertEqual(result, "10 seconds")
        
        # only minute
        result = seconds_to_readable(60)
        self.assertEqual(result, "1 minute")

        # minutes and seconds
        result = seconds_to_readable(122)
        self.assertEqual(result, "2 minutes, and 2 seconds")

        # minute and second
        result = seconds_to_readable(61)
        self.assertEqual(result, "1 minute, and 1 second")

        # hour and minutes
        result = seconds_to_readable(3660)
        self.assertEqual(result, "1 hour, 1 minute")

        # hours
        result = seconds_to_readable(7200)
        self.assertEqual(result, "2 hours")
