# Generated by Django 4.0.5 on 2022-07-05 10:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_alter_emergency_charge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='prescription',
            old_name='Count',
            new_name='count',
        ),
    ]
