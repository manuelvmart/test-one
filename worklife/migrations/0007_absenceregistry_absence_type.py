# Generated by Django 5.1.6 on 2025-02-25 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worklife', '0006_alter_vacationrequest_approved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='absenceregistry',
            name='absence_type',
            field=models.CharField(choices=[('0', 'Unjustified absences'), ('1', 'Justified absences')], max_length=1, null=True),
        ),
    ]
