# Generated manually for Phase 2.1 - Timetable

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0031_subject_examtype_examscore_dynamic'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('order', models.PositiveSmallIntegerField(default=0, help_text='Display order')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.school')),
            ],
            options={
                'ordering': ('order', 'start_time'),
            },
        ),
        migrations.CreateModel(
            name='TimetableEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.PositiveSmallIntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')])),
                ('class_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.classroom')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.school')),
                ('staff', models.ForeignKey(blank=True, help_text='Teacher', null=True, on_delete=django.db.models.deletion.SET_NULL, to='members.staff')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.subject')),
                ('time_slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.timeslot')),
            ],
            options={
                'verbose_name_plural': 'Timetable entries',
                'unique_together': {('school', 'class_room', 'day_of_week', 'time_slot')},
            },
        ),
    ]
