"""
Diagnostic: verify where Django finds Volt static files.
Run from project root: python manage.py check_static

Use this to confirm BASE_DIR and that assets/js/volt.js and css/volt.css
are found when runserver serves the dashboard. Only runs when DEBUG is True.
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.staticfiles.finders import find


class Command(BaseCommand):
    help = "Verify static file paths and Volt asset discovery (DEBUG only)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.WARNING(
                "check_static is a diagnostic for development. DEBUG is False; skipping."
            ))
            return

        base_dir = getattr(settings, "BASE_DIR", None)
        static_dirs = getattr(settings, "STATICFILES_DIRS", [])

        self.stdout.write("Static file diagnostic (Volt dashboard)")
        self.stdout.write("-" * 50)
        self.stdout.write(f"BASE_DIR: {base_dir}")
        self.stdout.write(f"STATICFILES_DIRS: {static_dirs}")
        self.stdout.write("")

        # Use find() to see what Django's static finders return
        for path in ["assets/js/volt.js", "css/volt.css"]:
            found = find(path)
            if found:
                self.stdout.write(self.style.SUCCESS(f"findstatic {path}: {found}"))
            else:
                self.stdout.write(self.style.ERROR(f"findstatic {path}: No matching file found"))

        # On-disk check under BASE_DIR/static
        if base_dir is not None:
            base = Path(base_dir)
            for rel in ["static/assets/js/volt.js", "static/css/volt.css"]:
                full = base / rel
                if full.exists():
                    self.stdout.write(self.style.SUCCESS(f"On disk: {full}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Missing on disk: {full}"))
        self.stdout.write("-" * 50)
