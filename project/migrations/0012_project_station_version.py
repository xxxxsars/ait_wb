# Generated by Django 2.2.5 on 2020-10-23 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0011_auto_20200312_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='project_station',
            name='version',
            field=models.CharField(max_length=50, null=True),
        ),
    ]