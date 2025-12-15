def get_requester_ip(request_object):
    ip_try = request_object.META.get("HTTP_X_FORWARDED_FOR")
    if ip_try:
        rip = ip_try.split(",")[0].strip()
    else:
        rip = request_object.META.get("REMOTE_ADDR")
    if not rip:
        rip = "0.0.0.0"
    return rip

def seconds_to_readable(time_in_seconds):
    hours, seconds = time_in_seconds // 3600, time_in_seconds % 3600
    minutes, secs = seconds // 60, seconds % 60
    return_str = ""
    if hours > 0:
        if hours == 1:
            return_str += f"{hours} hour"
        else:
            return_str += f"{hours} hours"
    if minutes > 0:
        minute_str = f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
        if "hour" in return_str:
            return_str += f", {minute_str}"
        else:
            return_str += minute_str
    if secs > 0:
        seconds_str = f"{secs} second" if secs == 1 else f"{secs} seconds"
        if "hour" in return_str or "minute" in return_str:
            return_str += f", and {seconds_str}"
        else:
            return_str += seconds_str
    return return_str
