# Generated by Django 5.1.2 on 2025-02-16 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='russian_first_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='user',
            name='russian_last_name',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
