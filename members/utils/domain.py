"""
Subdomain extraction for tenant resolution.
Supports localhost:8000 and school.localhost for local dev.
"""


def extract_subdomain(host_or_request):
    """
    Extract subdomain from host.

    - Accepts a Django request or a host string (e.g. "school.example.com" or "school.localhost:8000").
    - Returns the subdomain (first label) or None if no subdomain.

    Examples:
        localhost, 127.0.0.1          -> None
        school.localhost              -> "school"
        school.localhost:8000         -> "school"
        school.domain.com             -> "school"
        acme.example.com              -> "acme"
        www.domain.com                -> None (www treated as no tenant)
        example.com                   -> None
    """
    if hasattr(host_or_request, "get_host"):
        host = (host_or_request.get_host() or "").split(":")[0].lower()
    else:
        host = (str(host_or_request).strip()).split(":")[0].lower()

    labels = [p for p in host.split(".") if p]
    root_like = {"localhost", "127.0.0.1"}
    if host in root_like or len(labels) <= 1:
        return None

    # Render default domain (*.onrender.com) = single-tenant, no school subdomain
    if len(labels) >= 3 and labels[-2] == "onrender" and labels[-1] == "com":
        return None

    if len(labels) == 2 and labels[1] == "localhost":
        return labels[0]

    if len(labels) >= 3:
        sub = labels[0]
        if sub == "www":
            return None
        return sub

    return None


def build_school_base_url(request, code: str) -> str:
    """
    Build absolute URL for the root of a school's subdomain.
    Supports localhost (e.g. code.localhost:8000) and production domains.
    """
    host = request.get_host()
    if ":" in host:
        hostname, port = host.split(":", 1)
        new_host = f"{code}.{hostname}:{port}"
    else:
        new_host = f"{code}.{host}"
    scheme = "https" if request.is_secure() else "http"
    return f"{scheme}://{new_host}/"
