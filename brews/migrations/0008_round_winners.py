# Generated by Django 4.2 on 2023-04-30 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brews', '0007_alter_judgement_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='winners',
            field=models.ManyToManyField(to='brews.entry'),
        ),
    ]
