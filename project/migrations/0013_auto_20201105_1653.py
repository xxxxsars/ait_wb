# Generated by Django 2.2.5 on 2020-11-05 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0007_upload_testcase_create_user'),
        ('project', '0012_project_station_version'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='project_task',
            unique_together={('task_id', 'task_name')},
        ),
    ]
