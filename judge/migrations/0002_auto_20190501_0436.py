# Generated by Django 2.2 on 2019-04-30 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='enable_linter_score',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='contest',
            name='enable_poster_score',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='contest',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
