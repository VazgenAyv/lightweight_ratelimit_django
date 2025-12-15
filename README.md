# 📚 Django Lightweight Rate Limiter Documentation

The `django-lightweight-rate-limiter` package provides a simple, yet robust, decorator-based rate limiting solution for Django views, leveraging Django's native caching framework.

## 🛠️ Installation

```bash
pip install django-lightweight-rate-limiter
```
Ensure you have a cache configured in your settings.py (e.g., Redis, Memcached, or the Database backend).
```
Python# settings.py example
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-rate-limiter-id',
    }
}
```
🚀 Basic UsageApply the `@RateLimiter.view_rate_limit()` decorator to any view function.Example: Default Limit (50 calls per hour)By default, the limit is set to 50 calls per hour ("50/h") and is applied based on the User ID.Python# views.py

```
from lightweight_ratelimit_django import RateLimiter
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
```

# Assumes RateLimiter is imported from a local file or installed package
# This limits logged-in users to 50 requests per hour to this endpoint.
```
@login_required 
@RateLimiter.view_rate_limit()
def protected_api_view(request):
    """
    Limited by User ID: RL:USER:pk:/api/view:H
    """
    return JsonResponse({"status": "Success", "data": "Limited content"})
```

⚙️ Configuration & Arguments
The decorator accepts three main keyword arguments:ArgumentTypeDefaultDescriptionlimitstr"50/h"Defines the maximum number of calls and the reset period.methodslist["GET"]List of HTTP methods to apply the limit to (e.g., ["POST"]). Requests using other methods will pass through without a check.exclude_userboolFalseIf True, the limiter only uses the client's IP address, even if the user is logged in.Defining the Limit (limit format)The limit argument must be a string in the format "COUNT/TIME_UNIT":Time UnitDescription (Timeout)ExampleCache SuffixdDay (86,400 seconds)"1000/d":DhHour (3,600 seconds)"50/h":HmMinute (60 seconds)"10/m":MConfiguration ExamplesPython# Limits ALL POST requests to 5 per minute, based on IP address
`@RateLimiter.view_rate_limit(limit="5/m", methods=["POST"], exclude_user=True)`
```
def heavy_post_view(request):
    """
    Limited by IP: RL:IP:address:/path:M
    """
    return JsonResponse({"status": "Created"})
```

# Limits anonymous and logged-in users to 200 calls per day. 
# Logged-in users are tracked by their PK, anonymous users by IP.
```
@RateLimiter.view_rate_limit(limit="200/d")
def daily_limit_view(request):
    """
    Limited by User OR IP: RL:USER:pk:/path:D or RL:IP:address:/path:D
    """
    return JsonResponse({"status": "OK"})
```
🔒 Rate Limiting Logic (User vs. IP)
The package uses a clear priority mechanism to determine which cache key is used to track the limit. This ensures both authenticated and anonymous users are always limited correctly.
Decision Flow:
Check 1: User Limiting (Highest Priority)Condition: exclude_user is False AND the user is authenticated (request.user.pk exists).Key Used: User ID (RL:USER:pk:..).
Check 2: IP Limiting (Fallback)
Condition: Either exclude_user is True OR the user is anonymous (request.user.pk is None).
Key Used: Client's IP Address (RL:IP:address:..).
This dual-priority system prevents users from bypassing the limit by logging out, ensuring they are always restricted by the highest available identifier.Cache Key StructureLimits are stored in Django's cache using a unique, timestamped key:$$\text{RL:}\langle\text{TYPE}\rangle\text{:}\langle\text{ID}\rangle\text{:}\langle\text{PATH}\rangle\text{:}\langle\text{UNIT}\rangle$$🚨 Error Handling
429 Too Many Requests
When a user exceeds the limit, the decorator will immediately return a JSON response with the HTTP status code 429 Too Many Requests.The response body informs the client exactly when they can retry the request:
JSON{
    "error": "Request limit exceeded, try again in 59 minutes, and 30 seconds"
}
405 Method Not Allowed
If a request is made using an HTTP method not included in the methods list (e.g., a DELETE request when only ["GET"] is allowed), a 405 Method Not Allowed is returned.
400 Bad Request
If the limit string passed to the decorator is malformed (e.g., "50/x"), a 400 Bad Request is returned.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
