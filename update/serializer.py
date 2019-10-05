from rest_framework import serializers
import upload.models



class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model =upload.models.Upload_TestCase
        fields = "__all__"



