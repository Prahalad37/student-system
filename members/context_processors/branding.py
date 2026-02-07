from django.templatetags.static import static
from ..utils import get_current_school

def school_branding(request):
    """
    Context processor to make school branding details available globally.
    """
    school = get_current_school(request)
    
    # Defaults
    branding = {
        'SCHOOL_NAME': school.name if school else 'ABC School',
        'SCHOOL_LOGO': static('img/school_logo.png'), # Placeholder logo
        'THEME_COLOR': 'primary', # Bootstrap color class or hex
        'THEME_COLOR_HEX': '#4e73df', # SB Admin 2 Blue
    }
    
    # You can add logic here to fetch from a SchoolConfiguration model later
    
    return {'branding': branding}
