from .models import School, UserProfile

def get_current_school(request):
    """
    Returns the School object for the logged-in user.
    """
    if not request.user.is_authenticated:
        return None
    
    # CASE 1: Superuser (You) - Default to First School (Prahlad Academy)
    if request.user.is_superuser:
        return School.objects.first()
    
    # CASE 2: Staff/Teacher - Return their assigned School
    try:
        if hasattr(request.user, 'userprofile'):
            return request.user.userprofile.school
    except Exception:
        pass
        
    return None