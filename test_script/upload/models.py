from django.db import models
import datetime
# Create your models here.


class Upload_TestCase(models.Model):
    task_id = models.CharField(max_length=255, unique=True, primary_key=True)
    task_name = models.CharField(max_length=255, unique=True)
    sample = models.CharField(max_length=255,default="")
    description =  models.TextField()
    script_name = models.CharField(max_length=255)
    time = models.DateTimeField(default=datetime.datetime.now,blank=True)
    existed_attachment = models.BooleanField(default=False)
    modify_user =  models.CharField(max_length=50,default="")
    create_user =  models.CharField(max_length=50,default="")
    version =  models.CharField(max_length=50,default="0.01")

    class Meta:
        db_table = "test_case"


class Arguments(models.Model):
    task_id = models.ForeignKey(Upload_TestCase, on_delete=models.CASCADE)
    argument = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    default_value = models.CharField(max_length=255, default="null")

    class Meta:
        db_table = "arguments"

        unique_together = (('task_id', 'argument'),)
