# Generated by Django 4.2.6 on 2023-12-13 17:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_profile_post'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='image_url',
        ),
    ]