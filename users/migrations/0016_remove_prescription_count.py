# Generated by Django 4.0.5 on 2022-07-11 06:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_remove_customuser_role_fk_alter_customuser_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prescription',
            name='count',
        ),
    ]
