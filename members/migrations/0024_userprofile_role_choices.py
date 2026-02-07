from django.db import migrations, models


ROLE_CHOICES = [
    ("OWNER", "OWNER"),
    ("ADMIN", "ADMIN"),
    ("ACCOUNTANT", "ACCOUNTANT"),
    ("TEACHER", "TEACHER"),
    ("STAFF", "STAFF"),
]


def set_existing_roles_to_owner(apps, schema_editor):
    UserProfile = apps.get_model("members", "UserProfile")
    UserProfile.objects.all().update(role="OWNER")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0023_school_code_slug"),
    ]

    operations = [
        migrations.RunPython(set_existing_roles_to_owner, noop),
        migrations.AlterField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                choices=ROLE_CHOICES,
                default="OWNER",
                max_length=20,
            ),
        ),
    ]
