# Generated by Django 2.2.5 on 2019-10-21 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0002_arguments_default_value'),
        ('project', '0007_auto_20191021_1550'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='project_task_argument',
            unique_together={('task_id', 'argument')},
        ),
    ]
