# Generated by Django 4.2 on 2023-04-30 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brews', '0009_remove_round_winners_heat_winners_alter_heat_entries'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='entries',
            field=models.ManyToManyField(to='brews.entry'),
        ),
    ]