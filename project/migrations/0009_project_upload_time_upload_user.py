# Generated by Django 2.2.5 on 2020-03-02 10:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0008_auto_20200227_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='project_upload_time',
            name='upload_user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
