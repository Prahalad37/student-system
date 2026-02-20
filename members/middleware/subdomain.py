"""
Subdomain Middleware for Multi-Tenant School ERP System

This middleware extracts the school from the subdomain and attaches it to the request object.
It enables school-specific routing and context throughout the application.

URL Pattern:
- super-admin.schoolerp.local → Super Admin Portal  
- {school-code}.schoolerp.local → School Portal
"""

from django.http import Http404
from django.shortcuts import redirect
from members.models import School
from members.utils.branding import get_school_branding


class SubdomainMiddleware:
    """
    Middleware to handle subdomain-based multi-tenancy.
    
    For each request:
    1. Extract subdomain from host
    2. Determine if it's super-admin or school-specific  
    3. Load school and branding context
    4. Attach to request object for use in views
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract host and subdomain
        host = request.get_host().split(':')[0]  # Remove port if present
        parts = host.split('.')
        
        # Handle localhost and IP addresses (for development)
        if host in ['localhost', '127.0.0.1'] or host.startswith('192.168'):
            subdomain = 'localhost'
        else:
            subdomain = parts[0] if len(parts) > 1 else 'localhost'
        
        # Initialize default request attributes
        request.school = None
        request.is_super_admin_domain = False
        request.branding = None
        
        # Handle super-admin subdomain
        if subdomain == 'super-admin':
            request.is_super_admin_domain = True
            return self.get_response(request)
        
        # Handle localhost for development (no school restriction)
        if subdomain == 'localhost':
            # In development, determine school from session or URL params
            # For now, allow access without school context
            return self.get_response(request)
        
        # Handle school-specific subdomains
        try:
            school = School.objects.get(code=subdomain, is_active=True)
            request.school = school
            request.branding = get_school_branding(school)
        except School.DoesNotExist:
            # Invalid subdomain - show 404 or redirect to super admin
            raise Http404(f"School with code '{subdomain}' not found")
        
        return self.get_response(request)
