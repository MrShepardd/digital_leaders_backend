# Generated by Django 3.0.5 on 2020-10-03 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20201003_1258'),
    ]

    operations = [
        migrations.AddField(
            model_name='atmcrowdedplace',
            name='multi_line_string',
            field=models.TextField(default=''),
        ),
    ]
