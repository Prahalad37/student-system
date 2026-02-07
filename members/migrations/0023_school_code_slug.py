# Generated manually for subdomain-based tenant resolver

from django.db import migrations, models
from django.utils.text import slugify


def slugify_code(val: str) -> str:
    s = slugify(val) or "school"
    return s.lower()[:64]


def backfill_school_code(apps, schema_editor):
    School = apps.get_model("members", "School")
    seen = set()
    for s in School.objects.all():
        base = slugify_code(s.school_code)
        candidate = base
        n = 0
        while candidate in seen:
            n += 1
            candidate = f"{base}-{n}"[:64]
        seen.add(candidate)
        s.code = candidate
        s.save(update_fields=["code"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0022_finance_engine_v2_and_school_scope"),
    ]

    operations = [
        migrations.AddField(
            model_name="school",
            name="code",
            field=models.SlugField(
                blank=True,
                help_text="Lower, slug-friendly subdomain (e.g. acme)",
                max_length=64,
                null=True,
                unique=True,
            ),
        ),
        migrations.RunPython(backfill_school_code, noop),
        migrations.AlterField(
            model_name="school",
            name="code",
            field=models.SlugField(
                help_text="Lower, slug-friendly subdomain (e.g. acme)",
                max_length=64,
                unique=True,
            ),
        ),
    ]
