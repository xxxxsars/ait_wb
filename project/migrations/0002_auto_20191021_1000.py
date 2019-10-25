# Generated by Django 2.2.5 on 2019-10-21 02:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project_task',
            name='criteria',
            field=models.CharField(default='success', max_length=20),
        ),
        migrations.AddField(
            model_name='project_task',
            name='exit_code',
            field=models.CharField(default='exitCode', max_length=20),
        ),
        migrations.AddField(
            model_name='project_task',
            name='retry_count',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='project_task',
            name='sleep_time',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='project_task',
            name='timeout',
            field=models.IntegerField(default=30),
        ),
    ]
