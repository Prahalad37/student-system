from django.http import HttpResponseForbidden


# DEPRECATED: Use members.utils.role_guards.require_roles instead.
# This decorator uses Django groups; require_roles uses UserProfile.role (tenant-scoped).
def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.groups.filter(name__in=allowed_roles).exists() or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("You are not authorized to view this page.")
        return wrapper_func
    return decorator