from rest_framework import serializers
import upload.models



class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model =upload.models.Upload_TestCase
        fields = "__all__"



class ArgumentuSerializer(serializers.ModelSerializer):
    class Meta:
        model =upload.models.Arguments
        fields = "__all__"