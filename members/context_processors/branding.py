from django.templatetags.static import static

def school_branding(request):
    """
    Context processor to make school branding details available globally.
    On landing page: only Semora (no school name). Else: school name or Semora default.
    """
    # Landing page: always Semora only, no school name
    if getattr(request.resolver_match, "url_name", None) == "landing":
        branding = {
            "SCHOOL_NAME": "Semora",
            "SCHOOL_TAGLINE": "Optimize Operations, Elevate Education",
            "SCHOOL_LOGO": None,
            "THEME_COLOR": "primary",
            "THEME_COLOR_HEX": "#4e73df",
        }
        return {"branding": branding}

    school = getattr(request, "school", None)
    branding = {
        "SCHOOL_NAME": school.name if school else "Semora",
        "SCHOOL_TAGLINE": "Optimize Operations, Elevate Education",
        "SCHOOL_LOGO": None,
        "THEME_COLOR": "primary",
        "THEME_COLOR_HEX": "#4e73df",
    }
    return {"branding": branding}
