from django.db import models
from django.contrib.auth.models import User
from test_script.upload.models import *


# Create your models here.
class Project(models.Model):
    project_name = models.CharField(max_length=255, unique=True, primary_key=True)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project"


class Project_PN(models.Model):
    part_number = models.CharField(max_length=255)
    project_name = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Mega:
        db_table = "project_pn"
        unique_together = (('project_name', 'part_number'),)


class Project_Station(models.Model):
    project_pn_id = models.ForeignKey(Project_PN, on_delete=models.CASCADE)
    station_name = models.CharField(max_length=255)

    class Mega:
        db_table = "project_station"
        unique_together = (('project_pn_id', 'station_name'),)


class Project_task(models.Model):
    station_id = models.ForeignKey(Project_Station, on_delete=models.CASCADE)
    task_id = models.ForeignKey(Upload_TestCase, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    timeout = models.IntegerField(default=30)
    exit_code = models.CharField(max_length=20, default="exitCode")
    retry_count = models.IntegerField(default=3)
    sleep_time = models.IntegerField(default=0)
    criteria = models.CharField(max_length=20, default="success")

    class Meta:
        db_table = "project_task"
        # unique_together = (('task_id', 'station_id'),)   #remove this line



class Project_task_argument(models.Model):
    default_value = models.CharField(max_length=255, default="null")
    argument = models.ForeignKey(Arguments, on_delete=models.CASCADE)
    station_id = models.ForeignKey(Project_Station, on_delete=models.CASCADE)
    task_id = models.ForeignKey(Upload_TestCase, on_delete=models.CASCADE)
    project_task_id = models.ForeignKey(Project_task, on_delete=models.CASCADE)

    class Meta:
        db_table = "project_task_arguments"
        unique_together = (('project_task_id', 'argument',),)


class Project_TestScript_order(models.Model):
    station_name = models.ForeignKey(Project_Station, on_delete=models.CASCADE)
    part_number = models.ForeignKey(Project_PN, on_delete=models.CASCADE)
    project_name = models.ForeignKey(Project, on_delete=models.CASCADE)

    script_oder = models.CharField(max_length=255)

    class Meta:
        db_table = "project_script_order"

        unique_together = (('project_name', 'part_number'),)