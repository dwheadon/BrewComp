# Generated by Django 4.2 on 2023-04-30 03:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('brews', '0003_remove_competition_open_competition_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='label',
            field=models.CharField(max_length=1),
        ),
        migrations.CreateModel(
            name='Heat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round', models.PositiveSmallIntegerField()),
                ('label', models.CharField(max_length=1)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brews.competition')),
            ],
            options={
                'ordering': ['competition', 'round', 'label'],
            },
        ),
    ]
