# Generated by Django 4.1.2 on 2023-04-23 04:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('brews', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='judges',
        ),
    ]
