# Generated by Django 4.0.5 on 2022-06-29 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile',
            field=models.ImageField(blank=True, default='default.jpg', null=True, upload_to='profile_pic/'),
        ),
    ]
