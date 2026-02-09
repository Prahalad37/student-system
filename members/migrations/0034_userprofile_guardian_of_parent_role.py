# Generated manually for Phase 2.3 - Parent portal

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0033_admissionenquiry'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='guardian_of',
            field=models.ManyToManyField(blank=True, help_text='Linked students when role=PARENT', related_name='guardians', to='members.member'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('OWNER', 'OWNER'), ('ADMIN', 'ADMIN'), ('ACCOUNTANT', 'ACCOUNTANT'), ('TEACHER', 'TEACHER'), ('STAFF', 'STAFF'), ('STUDENT', 'STUDENT'), ('PARENT', 'PARENT')], default='OWNER', max_length=20),
        ),
    ]
