from rest_framework import serializers
import  test_script.upload.models



class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model= test_script.upload.models.Upload_TestCase
        fields = "__all__"
