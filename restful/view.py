import os

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.shortcuts import redirect


import zipfile, os, shutil, platform

from update.forms import *
from update.serializer import *
from update.models import *

from common.limit import input_argument





class DeleteTestCaseView(viewsets.ModelViewSet):
    queryset = Upload_TestCase.objects.all()
    serializer_class = TaskSerializer
    http_method_names = ['delete']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            task_name = serializer.data["task_name"]
            remove_upload_file(task_name)
            self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)

def vail_argument(argument):
    r = input_argument
    if r.search(argument) != None:
        return False
    return True

# handle_update_file will remove all unzip folder
def handle_update_file(f, task_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        source_zip = path + r'\upload_folder\\' + f.name
        unzip_path = path + r'\upload_folder\\'

    else:
        source_zip = path + '/upload_folder/' + f.name
        unzip_path = path + '/upload_folder/'

    with open(source_zip, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # check vaild zip file
    try:
        zip_file = zipfile.ZipFile(source_zip)
        ret = zip_file.testzip()

        if ret is not None:
            raise Exception("not valid zip")
        zip_file.close()
    except Exception:
        os.remove(source_zip)
        raise Exception("Upload file is no valid zip file.")

    # remove old script file
    try:
        shutil.rmtree(unzip_path + task_name)
    except Exception:
        pass

    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(unzip_path + task_name)

    os.remove(source_zip)



def remove_upload_file(task_name):
    path = os.path.dirname(  os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        source_folder = path + r'\upload_folder\\' + task_name

    else:
        source_folder = path+'/upload_folder/' + task_name


    # remove  script file
    try:
        shutil.rmtree(source_folder )
    except Exception:
        pass

