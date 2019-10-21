from django.db import models
from django.contrib.auth.models import User
from test_script.upload.models  import *

# Create your models here.
class Project(models.Model):
    project_name = models.CharField(max_length=255,unique=True,primary_key=True)
    owner_user =models.ForeignKey(User,on_delete=models.CASCADE)

    class Meta:
        db_table = "project"


class Project_task(models.Model):
    project_name =models.ForeignKey(Project,on_delete=models.CASCADE)
    task_id = models.ForeignKey(Upload_TestCase,on_delete=models.CASCADE)

    timeout = models.IntegerField(default=30)
    exit_code = models.CharField(max_length=20,default="exitCode")
    retry_count = models.IntegerField(default=3)
    sleep_time = models.IntegerField(default=0)
    criteria = models.CharField(max_length=20,default="success")

    class Meta:
        db_table = "project_task"
        unique_together = (('task_id','project_name'),)



class Project_task_argument(models.Model):
    argument = models.CharField(max_length=255)
    default_value = models.CharField(max_length=255,default="null")

    project_name =models.ForeignKey(Project,on_delete=models.CASCADE)
    task_id = models.ForeignKey(Upload_TestCase,on_delete=models.CASCADE)


    class Meta:
        db_table = "project_task_arguments"
        unique_together = (('task_id','project_name','argument'),)




class Download_log(models.Model):
    token  = models.CharField(max_length=30,primary_key=True)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table ="download_log"