# Generated by Django 4.2 on 2023-05-01 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brews', '0012_alter_heat_options_remove_heat_label_heat_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='heat',
            name='criteria',
            field=models.ManyToManyField(blank=True, to='brews.criterion'),
        ),
    ]
