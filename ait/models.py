from django.db import models

# Create your models here.

class AIT_release(models.Model):
    version = models.CharField(max_length=255,unique=True)
    release_note = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = "ait_release"