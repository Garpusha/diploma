# Generated by Django 4.2.1 on 2023-11-18 13:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("backend", "0004_store_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="temp_token",
            field=models.CharField(blank=True, max_length=32),
        ),
    ]