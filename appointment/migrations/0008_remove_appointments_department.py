# Generated by Django 4.0.5 on 2022-06-25 19:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0007_alter_appointments_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointments',
            name='department',
        ),
    ]