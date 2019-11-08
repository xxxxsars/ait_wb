from rest_framework import serializers
from project.models import *


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"



class ProjectTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project_task
        fields = "__all__"