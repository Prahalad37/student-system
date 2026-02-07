"""View and access control tests."""
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from ..models import School, UserProfile


class DashboardAccessTest(TestCase):
    """Test dashboard and role-based access."""

    def setUp(self):
        self.school = School.objects.create(
            name="Test School",
            address="123 Test St",
            school_code="TEST001",
            code="test",
        )
        self.user = User.objects.create_user(username="owner", password="testpass123")
        UserProfile.objects.filter(user=self.user).update(
            school=self.school,
            role="OWNER",
        )

    def test_login_required_redirects_anonymous(self):
        client = Client()
        # On localhost, TenantMiddleware sets school to first school
        resp = client.get("/")
        self.assertIn(resp.status_code, [302, 403])  # Redirect to login or 403

    def test_authenticated_user_can_access_dashboard(self):
        client = Client()
        client.force_login(self.user)
        resp = client.get("/", HTTP_HOST="test.localhost:8000")
        self.assertEqual(resp.status_code, 200)
