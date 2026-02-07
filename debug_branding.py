import os
import django
from django.conf import settings
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from members.models import School
from members.context_processors.branding import school_branding

print("--- DB CHECK ---")
school = School.objects.first()
if school:
    print(f"School Found: ID={school.id}, Name='{school.name}', Code='{school.code}'")
else:
    print("No School found in DB.")

print("\n--- CONTEXT PROCESSOR CHECK ---")
factory = RequestFactory()
request = factory.get('/')
# Simulate TenantMiddleware logic
if school:
    request.school = school
else:
    request.school = None

ctx = school_branding(request)
print(f"Branding Context: {ctx}")
