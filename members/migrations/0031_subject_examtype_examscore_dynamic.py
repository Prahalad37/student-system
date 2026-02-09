# Generated manually for Phase 1.4 - configurable subjects and exam types

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0030_add_getting_started_dismissed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(blank=True, max_length=20)),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='members.school')),
            ],
            options={
                'unique_together': {('school', 'name')},
            },
        ),
        migrations.CreateModel(
            name='ExamType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='members.school')),
            ],
        ),
        migrations.AddField(
            model_name='examscore',
            name='exam_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='members.examtype'),
        ),
        migrations.AddField(
            model_name='examscore',
            name='subject_marks',
            field=models.JSONField(blank=True, help_text='e.g. {"Maths": 85, "Physics": 90}', null=True),
        ),
    ]
