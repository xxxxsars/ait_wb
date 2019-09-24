from django.db import models

# Create your models here.


class Upload_TestCase(models.Model):
    task_id =  models.CharField(max_length=255,unique=True)
    script_name =  models.CharField(max_length=255,unique=True)
    description =  models.CharField(max_length=255)
    exec_time =  models.IntegerField()
    argument =  models.CharField(max_length=255)



    class Meta:
        db_table = "up_testcase"