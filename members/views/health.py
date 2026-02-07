"""Health check endpoint for load balancers and PaaS platforms."""
from django.http import HttpResponse


def health(request):
    """Returns 200 OK - no auth, no tenant required."""
    return HttpResponse("OK", content_type="text/plain")
