import os
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


from io import StringIO,BytesIO
import zipfile, os, shutil, platform

from test_script.update.forms import *
from test_script.restful.serializer import *

from common.handler import handle_path

from django.contrib.auth import login
@api_view(["POST"])
@authentication_classes((BasicAuthentication,SessionAuthentication))
def delete_attachment(request):
    if request.method == "POST":
        task_ids = [ u.task_id  for u in Upload_TestCase.objects.all() ]
        if "task_id" not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        task_id = request.data.get("task_id")
        if task_id not in task_ids:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        task_instance = Upload_TestCase.objects.get(task_id=task_id)
        task_instance.existed_attachment = False

        path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        remove_path = handle_path(path, "upload_folder",task_id,"attachment")
        shutil.rmtree(remove_path)

        task_instance.save()
        return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes((BasicAuthentication,SessionAuthentication))
def script_download(request,task_id):
    if request.method == "GET":
        path = handle_path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           "upload_folder", task_id)

        attach_path = os.path.join(path,'attachment')
        s = BytesIO()
        zf = zipfile.ZipFile(s, "w", compression=zipfile.ZIP_DEFLATED)

        # the array inner dict key is source file path ,value is target file path
        for root, folders, files in os.walk(path):
            for sfile in files:
                if root!= attach_path:
                    aFile = os.path.join(root, sfile)
                    zf.write(aFile, os.path.relpath(aFile, path))
        zf.close()
        response = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % task_id
        response['Content-Length'] = s.tell()

        return response

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes((BasicAuthentication,SessionAuthentication))
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
        return Response(status=status.HTTP_200_OK)


class DeleteTestCaseView(viewsets.ModelViewSet):
    queryset = Upload_TestCase.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [BasicAuthentication,]
    permission_classes = [IsAdminUser,]
    http_method_names = ['delete']

    # permission_classes = (IsAdminUser,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            task_id = serializer.data["task_id"]
            remove_upload_file(task_id)
            self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


def remove_upload_file(task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    source_folder = os.path.join(handle_path(path, "upload_folder"), task_id)

    # remove  script file
    try:
        shutil.rmtree(source_folder)
    except Exception:
        pass


@login_required(login_url="/user/login/")
def attach_download(request,task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_root = handle_path(path,"upload_folder",task_id,"attachment")


    files =[f for f in os.listdir(file_root) if os.path.isfile(os.path.join(file_root,f))]


    file_name = files[0]

    file = open(os.path.join(file_root,file_name), 'rb')
    response = StreamingHttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"'%file_name
    return response


@login_required(login_url="/user/login/")
def valid_script_name(request):
    if request.GET:
        task_name = request.GET["task_name"]
        if Upload_TestCase.objects.filter(task_name=task_name).count():
            return JsonResponse({"valid":False})
        else:
            return JsonResponse({"valid": True})
