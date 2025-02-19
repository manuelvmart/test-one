# Generated by Django 5.1.6 on 2025-02-19 18:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worklife', '0005_vacationrequest'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacationrequest',
            name='approved',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='workincident',
            name='applied',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='workincident',
            name='incident_type',
            field=models.CharField(choices=[('0', 'Vacations'), ('2', 'Delay'), ('3', 'Unjustified absences'), ('4', 'Justified absences'), ('5', 'Maternity leave'), ('6', 'Work Incapacity')], max_length=1),
        ),
        migrations.AlterField(
            model_name='worktimeperiod',
            name='date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='WorkTime'),
        ),
        migrations.CreateModel(
            name='AbsenceRegistry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('absence_start', models.DateTimeField(verbose_name='AbsenceStartTime')),
                ('absence_end', models.DateTimeField(verbose_name='AbsenceStartTime')),
                ('detail', models.CharField(max_length=200)),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='worklife.workincident')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
