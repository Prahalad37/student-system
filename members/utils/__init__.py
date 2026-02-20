# Utils package for members app

from .domain import extract_subdomain, build_school_base_url


def get_current_school(request):
    """Get the current school from request user's profile"""
    if hasattr(request, 'user') and request.user.is_authenticated:
        if hasattr(request.user, 'userprofile') and request.user.userprofile.school:
            return request.user.userprofile.school
    
    # Fallback: get first school if exists
    from members.models import School
    return School.objects.first()


__all__ = [
    'extract_subdomain',
    'build_school_base_url',
    'get_current_school',
]
