# Generated by Django 2.2.5 on 2020-02-27 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_auto_20200103_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='project_upload_time',
            name='upload_message',
            field=models.BooleanField(default=False, max_length=255),
        ),
    ]
