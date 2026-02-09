# Generated manually for School ERP plan Phase 1.2

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0029_add_student_role_and_member'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='getting_started_dismissed',
            field=models.BooleanField(default=False, help_text="Dismiss 'getting started' banner on dashboard"),
        ),
    ]
