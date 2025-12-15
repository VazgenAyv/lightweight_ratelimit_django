from django.core.cache import cache
from functools import wraps
import re
from django.http import JsonResponse
from lightweight_ratelimit_django.rate_limiter.utils.utils import (
    get_requester_ip,
    seconds_to_readable
)

class RateLimiter:
    default_limit = "50/h" # 50 calls per hour
    default_method = ["GET"]

    @classmethod
    def __validate_limiter_input(cls, inp):
        if not isinstance(inp, str) or not re.match("^\d+/(d|h|m)$", inp):
            return False
        return True

    @classmethod
    def limit_type(cls, the_input):
        call_count, reset_type = the_input.split("/")
        if reset_type == "d":
            timeout = 86400
            type_ = "D"
        elif reset_type == "h":
            timeout = 3600
            type_ = "H"
        else:
            timeout = 60
            type_ = "M"
        return {
            "count": int(call_count),
            "timeout": timeout,
            "type": type_
        }
    
    @classmethod
    def _check_and_update_limits(cls, cache_key, limit):
        limit_details = cls.limit_type(limit)
        remaining = cache.get(f"{cache_key}:{limit_details['type']}")
        if remaining is None:
            cache.set(f"{cache_key}:{limit_details['type']}", limit_details['count'] - 1, limit_details['timeout'])
            return
        else:
            remaining -= 1
            remaining_timout = cache.ttl(f"{cache_key}:{limit_details['type']}")

            if remaining < 0:
                return JsonResponse(
                    {
                        "error": f"Request limit exceeded, try again in {seconds_to_readable(remaining_timout)}"
                    },
                    status=429
                )
            
            cache.set(f"{cache_key}:{limit_details['type']}", remaining, timeout=remaining_timout)
            return
    
    @classmethod
    def view_rate_limit(cls, **kw):
        def view_limiter(view_func):
            @wraps(view_func)
            def wrapper(request, *args, **kwargs):
                methods = kw.get("methods") or cls.default_method
                if request.method not in methods:
                    return JsonResponse(
                        {
                            "error": "Method not allowed"
                        },
                        status=405
                    )
                limiter = kw.get("limit") or cls.default_limit
                if not cls.__validate_limiter_input(limiter):
                    return JsonResponse(
                        {
                            "error": "Wrongly formed limiter, must be \"{count of calls}/(d or h or m)\""
                        },
                        status=400
                    )
                exclude_user = kw.get("exclude_user", False)
                user_ip = get_requester_ip(request)
                user_key = getattr(request.user, "pk", None)

                # User based limiter
                if not exclude_user and user_key is not None:
                    cache_key = f"RL:USER:{user_key}:{request.path}"

                #ip based limiter
                else:
                    cache_key = f"RL:IP:{user_ip}:{request.path}"

                
                result = cls._check_and_update_limits(cache_key, limiter)
                if result:
                    return result
                return view_func(request, *args, **kwargs)
            return wrapper
        return view_limiter 
