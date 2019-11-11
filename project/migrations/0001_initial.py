# Generated by Django 2.2.5 on 2019-11-08 14:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('upload', '0004_upload_testcase_sample'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('project_name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('owner_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'project',
            },
        ),
        migrations.CreateModel(
            name='Project_PN',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_number', models.CharField(max_length=255)),
                ('project_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Project_Station',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_name', models.CharField(max_length=255)),
                ('project_pn_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project_PN')),
            ],
        ),
        migrations.CreateModel(
            name='Project_task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=255)),
                ('timeout', models.IntegerField(default=30)),
                ('exit_code', models.CharField(default='exitCode', max_length=20)),
                ('retry_count', models.IntegerField(default=3)),
                ('sleep_time', models.IntegerField(default=0)),
                ('criteria', models.CharField(default='success', max_length=20)),
                ('station_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project_Station')),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.Upload_TestCase')),
            ],
            options={
                'db_table': 'project_task',
            },
        ),
        migrations.CreateModel(
            name='Project_TestScript_order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('script_oder', models.CharField(max_length=255)),
                ('part_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project_PN')),
                ('project_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project')),
                ('station_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project_Station')),
            ],
            options={
                'db_table': 'project_script_order',
                'unique_together': {('project_name', 'part_number')},
            },
        ),
        migrations.CreateModel(
            name='Project_task_argument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_value', models.CharField(default='null', max_length=255)),
                ('argument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.Arguments')),
                ('project_task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project_task')),
                ('station_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project_Station')),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.Upload_TestCase')),
            ],
            options={
                'db_table': 'project_task_arguments',
                'unique_together': {('project_task_id', 'argument')},
            },
        ),
    ]
