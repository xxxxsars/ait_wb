from rest_framework import serializers
from project.models import *


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"



class ProjectPNSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project_PN
        fields = "__all__"