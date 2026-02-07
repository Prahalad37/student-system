"""
Subdomain-based tenant resolution with localhost fallback.
Maps subdomain -> School.code, sets request.school.
Attaches request.role for authenticated tenant requests.

FOR DEVELOPMENT: When no subdomain (localhost), auto-assigns first school.
"""

from __future__ import annotations

from django.http import Http404, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

from ..utils.domain import extract_subdomain
from ..models import School, ROLE_CHOICES

_VALID_ROLES = frozenset(c[0] for c in ROLE_CHOICES)


class TenantMiddleware(MiddlewareMixin):
    """
    Subdomain-based tenant identity with localhost development support.
    
    - With subdomain: Sets request.school from subdomain; 404 when subdomain unknown.
    - Without subdomain (localhost): Auto-assigns first school from UserProfile for development.
    - For authenticated users: sets request.role from UserProfile.
    """

    def process_request(self, request):
        path = (request.path or "").strip("/")
        if path.startswith("admin") or path == "health":
            request.school = None
            request.role = None
            return None
        subdomain = extract_subdomain(request)
        user = getattr(request, "user", None)
        is_authenticated = user and getattr(user, "is_authenticated", False)

        # Case 1: No subdomain (localhost development)
        # Case 1: No subdomain (localhost development)
        if subdomain is None:
            # Default to first school for localhost (Dev Mode)
            first_school = School.objects.first()
            request.school = first_school

            # For authenticated users, override with their profile school if exists
            if is_authenticated:
                profile = getattr(user, "userprofile", None)
                if profile:
                    request.school = profile.school
                    request.role = "OWNER" if getattr(user, "is_superuser", False) else profile.role
                    return None
                
                # No profile - fallback to first school (already set)
                request.role = "OWNER" if getattr(user, "is_superuser", False) else None
                return None
            
            # Not authenticated on localhost
            request.role = None
            return None

        # Case 2: With subdomain (production multi-tenant)
        school = School.objects.filter(code=subdomain.lower()).first()
        if not school:
            raise Http404("Tenant not found")

        request.school = school

        # Set role for authenticated users
        if not is_authenticated:
            return None

        profile = getattr(user, "userprofile", None)
        if not profile:
            return HttpResponseForbidden("No user profile")
        if profile.school_id != school.id:
            raise Http404("Wrong tenant")
        if profile.role not in _VALID_ROLES:
            return HttpResponseForbidden("Invalid role")

        request.role = "OWNER" if getattr(user, "is_superuser", False) else profile.role
        return None
