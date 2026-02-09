# Generated manually for Phase 2.2 - Admission CRM

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0032_timetable_timeslot_timetableentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdmissionEnquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('class_applying', models.CharField(blank=True, help_text='Class applying for', max_length=50)),
                ('source', models.CharField(blank=True, help_text='e.g. Website, Referral', max_length=100)),
                ('status', models.CharField(choices=[('New', 'New'), ('Contacted', 'Contacted'), ('Visited', 'Visited'), ('Admitted', 'Admitted'), ('Lost', 'Lost')], default='New', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.school')),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name_plural': 'Admission enquiries',
            },
        ),
    ]
