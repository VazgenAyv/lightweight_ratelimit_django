# 🚦 lightweight-ratelimit-django

A lightweight, decorator-based rate limiting solution for Django views, backed by Django’s cache framework and designed for accuracy, simplicity, and low overhead.

This package enforces request limits using strict TTL-based expiration, making it suitable for APIs and critical endpoints.

---

## ✨ Features

- Decorator-based rate limiting for Django views
- Supports authenticated users and anonymous IP-based limiting
- Accurate retry-after timing
- No middleware required
- Redis / Memcached compatible
- Minimal configuration

---

## 📦 Installation
```
pip install lightweight-ratelimit-django
```
---

## ⚠️ Cache Backend Requirements (IMPORTANT)

This package requires a cache backend with strict TTL enforcement.
This package relies on cache key TTL to calculate accurate retry-after timing.

### ❌ Unsupported Backends

The following backends are not supported and will break rate limiting logic:

- LocMemCache
  - Will result `AttributeError: 'LocMemCache' object has no attribute 'ttl'`

Do not use LocMemCache, even in development, since **package relies on cache key TTL to calculate accurate retry-after timing.**

### ✅ Supported Backends

- Redis (django-redis) – recommended (created with `Redis` in mind)
- Memcached
- Database cache (acceptable but slower)

---

## 🔧 Redis Configuration Example
```
# settings.py

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```
---

## 🚀 Basic Usage
```
from lightweight_ratelimit_django import RateLimiter
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
@RateLimiter.view_rate_limit()
def protected_api_view(request):
    return JsonResponse({"status": "success"})
```

### Defaults
- Default method: `GET`
- Default limit: `50/h`
- Default `exclude_user=False` (meaning if the request.user is logged in, limit will be calculated on the user)

## Example with custom configuration
```
@RateLimiter.view_rate_limit(limit="10/m", methods=["POST"], exclude_user=True)
def create_resource(request):
    return JsonResponse({"status": "created"})
```

---

## 📄 License

MIT License
