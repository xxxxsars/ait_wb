import os

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

import zipfile, os, shutil, platform

from test_script.update.forms import *
from test_script.update.serializer import *



@api_view(["POST"])
@authentication_classes((BasicAuthentication,))
def DeleteArgumentView(request, format=None):
    if request.method == "POST":
        task_id = request.data.get("task_id")
        argument = request.data.get("argument")

        if task_id == None or argument == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        task_args = Arguments.objects.filter(task_id=task_id)

        existed = task_args.filter(argument=argument).exists()

        if existed == False:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        arg_obj = task_args.get(argument=argument)
        arg_obj.delete()
        # arg_obj.save()
        return Response(status=status.HTTP_200_OK)



class DeleteTestCaseView(viewsets.ModelViewSet):
    queryset = Upload_TestCase.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [ BasicAuthentication]
    # permission_classes = (IsAdminUser,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            task_name = serializer.data["task_name"]
            remove_upload_file(task_name)
            self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


def remove_upload_file(task_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        source_folder = path + r'\upload_folder\\' + task_name

    else:
        source_folder = path + '/upload_folder/' + task_name

    # remove  script file
    try:
        shutil.rmtree(source_folder)
    except Exception:
        pass
