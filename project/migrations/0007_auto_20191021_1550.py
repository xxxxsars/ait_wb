# Generated by Django 2.2.5 on 2019-10-21 07:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('upload', '0002_arguments_default_value'),
        ('project', '0006_auto_20191021_1520'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='project_task',
            unique_together={('task_id', 'project_name')},
        ),
        migrations.AlterUniqueTogether(
            name='project_task_argument',
            unique_together={('task_id', 'project_name')},
        ),
    ]
