"""
Tenant-scoped role helpers (read-only).
Use these instead of touching role strings directly.
"""

from __future__ import annotations


def get_user_role(request) -> str | None:
    """
    Return the request's user role when tenant-scoped and authenticated.
    None if not authenticated, no tenant, or role not set.
    Superuser is treated as OWNER.
    """
    if not getattr(request, "user", None) or not getattr(
        request.user, "is_authenticated", False
    ):
        return None
    if getattr(request, "school", None) is None:
        return None
    if getattr(request.user, "is_superuser", False):
        return "OWNER"
    return getattr(request, "role", None)


def is_owner(request) -> bool:
    return get_user_role(request) == "OWNER"


def is_admin(request) -> bool:
    r = get_user_role(request)
    return r in ("OWNER", "ADMIN")
