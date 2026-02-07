from django.http import Http404


def get_current_school(request):
    school = getattr(request, "school", None)
    if not school:
        raise Http404("Tenant not resolved")
    return school
