from django.templatetags.static import static

def school_branding(request):
    """
    Context processor to make school branding details available globally.
    Uses defaults when no tenant (request.school None) e.g. marketing, error pages, fresh deploy.
    """
    school = getattr(request, "school", None)

    # Defaults
    branding = {
        'SCHOOL_NAME': school.name if school else 'ABC School',
        'SCHOOL_LOGO': None,  # Use generic icon - schools can upload custom logo later
        'THEME_COLOR': 'primary', # Bootstrap color class or hex
        'THEME_COLOR_HEX': '#4e73df', # SB Admin 2 Blue
    }
    
    # You can add logic here to fetch from a SchoolConfiguration model later
    
    return {'branding': branding}
