# Generated by Django 2.2.5 on 2019-10-21 07:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('upload', '0002_arguments_default_value'),
        ('project', '0005_auto_20191021_1514'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='project_task',
            unique_together={('project_name', 'task_id')},
        ),
        migrations.AlterUniqueTogether(
            name='project_task_argument',
            unique_together={('project_name', 'task_id')},
        ),
    ]
