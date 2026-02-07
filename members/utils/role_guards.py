from functools import wraps
from django.http import HttpResponseForbidden

from .roles import get_user_role


def require_roles(*allowed_roles):
    """
    Restrict access to users whose role is in allowed_roles.
    Usage:
        @require_roles("OWNER", "ADMIN")
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            role = get_user_role(request)

            if role is None:
                return HttpResponseForbidden("Role not resolved")

            if role not in allowed_roles:
                return HttpResponseForbidden("Insufficient role")

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
