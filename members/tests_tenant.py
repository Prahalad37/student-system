"""
Verification tests for subdomain-based tenant resolver.

Checklist:
- School.code exists and is unique
- TenantMiddleware sets request.school
- extract_subdomain: school.domain.com, school.localhost, www.domain.com (no tenant)
- Public root does not bind a tenant
- Root pages (index, login, login_redirect) do not use get_current_school when request.school missing
"""

from unittest.mock import Mock

from django.test import TestCase, RequestFactory
from django.http import Http404

from members.models import School
from members.utils.domain import extract_subdomain
from members.middleware.tenant import TenantMiddleware


# --- extract_subdomain ---


class ExtractSubdomainTests(TestCase):
    """Verify extract_subdomain for school.domain.com, school.localhost, www.domain.com."""

    def test_school_domain_com(self):
        self.assertEqual(extract_subdomain("school.domain.com"), "school")
        self.assertEqual(extract_subdomain("acme.example.com"), "acme")

    def test_school_localhost(self):
        self.assertEqual(extract_subdomain("school.localhost"), "school")
        self.assertEqual(extract_subdomain("school.localhost:8000"), "school")

    def test_www_domain_com_no_tenant(self):
        self.assertIsNone(extract_subdomain("www.domain.com"))
        self.assertIsNone(extract_subdomain("www.example.com"))

    def test_root_no_subdomain(self):
        self.assertIsNone(extract_subdomain("localhost"))
        self.assertIsNone(extract_subdomain("127.0.0.1"))
        self.assertIsNone(extract_subdomain("example.com"))
        self.assertIsNone(extract_subdomain("domain.com"))

    def test_request_object(self):
        req = Mock()
        req.get_host = Mock(return_value="school.localhost:8000")
        self.assertEqual(extract_subdomain(req), "school")


# --- School.code unique ---


class SchoolCodeTests(TestCase):
    """Verify School.code exists and is unique."""

    def test_code_field_exists_and_unique(self):
        self.assertTrue(hasattr(School, "code"))
        field = School._meta.get_field("code")
        self.assertTrue(field.unique)


# --- TenantMiddleware request.school ---


class TenantMiddlewareTests(TestCase):
    """Verify TenantMiddleware sets request.school; root does not bind tenant."""

    def setUp(self):
        self.factory = RequestFactory()
        self.mw = TenantMiddleware(lambda r: None)

    def _host_request(self, host, path="/"):
        req = self.factory.get(path)
        req.get_host = Mock(return_value=host)
        req.user = Mock(is_authenticated=False, is_superuser=False)
        return req

    def test_no_subdomain_sets_school_none(self):
        """Public root does not bind a tenant."""
        for host in ("localhost", "localhost:8000", "127.0.0.1", "example.com", "www.domain.com"):
            req = self._host_request(host)
            self.mw.process_request(req)
            self.assertIsNone(getattr(req, "school", "MISSING"))

    def test_subdomain_sets_school_when_code_exists(self):
        """TenantMiddleware loads request.school for matching subdomain."""
        school = School.objects.create(
            name="Test School",
            address="Somewhere",
            school_code="SC001",
            code="testschool",
        )
        req = self._host_request("testschool.localhost:8000")
        self.mw.process_request(req)
        self.assertIsNotNone(req.school)
        self.assertEqual(req.school.id, school.id)

    def test_subdomain_unknown_404(self):
        """Unknown subdomain -> 404."""
        req = self._host_request("nonexistent.localhost:8000")
        with self.assertRaises(Http404):
            self.mw.process_request(req)


# --- Root views never break when request.school missing ---


class RootViewsNoSchoolTests(TestCase):
    """Views reachable on root must not use get_current_school when request.school is missing."""

    def test_index_no_school_returns_marketing(self):
        """Index on root renders marketing, does not call get_current_school."""
        from members.views.dashboard import index

        req = RequestFactory().get("/")
        req.school = None
        req.user = Mock(is_authenticated=False)
        r = index(req)
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(getattr(req, "school", None))
        self.assertIn(b"Prahlad Academy ERP", r.content)
        self.assertIn(b"Log in", r.content)

    def test_auth_view_does_not_use_get_current_school(self):
        """login_redirect uses getattr only; root pages must not call get_current_school."""
        from pathlib import Path

        auth_py = Path(__file__).resolve().parent / "views" / "auth.py"
        content = auth_py.read_text()
        self.assertNotIn("get_current_school", content)
