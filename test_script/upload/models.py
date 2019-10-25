from django.db import models


# Create your models here.


class Upload_TestCase(models.Model):
    task_id = models.CharField(max_length=255, unique=True, primary_key=True)
    task_name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)
    script_name = models.CharField(max_length=255)

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
