# Generated by Django 2.2.5 on 2019-12-31 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0006_auto_20191231_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='upload_testcase',
            name='create_user',
            field=models.CharField(default='', max_length=50),
        ),
    ]