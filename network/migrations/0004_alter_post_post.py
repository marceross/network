# Generated by Django 4.2.6 on 2023-12-13 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_remove_post_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post',
            field=models.CharField(blank=True, max_length=280, null=True),
        ),
    ]
