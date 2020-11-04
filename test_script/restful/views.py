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

from common.handler import *

from django.contrib.auth import login
@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def delete_attachment_view(request):
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
        remove_path = handle_path(path, "upload_files",task_id,"attachment")
        shutil.rmtree(remove_path)

        task_instance.save()
        return Response(status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def script_download_view(request,task_id):
    if request.method == "GET":
        # update  python script version
        update_script_version(task_id)
        upload_path = handle_path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           "upload_files")
        test_case_path = handle_path(upload_path,task_id)

        attach_path = os.path.join(test_case_path,'attachment')
        s = BytesIO()
        zf = zipfile.ZipFile(s, "w", compression=zipfile.ZIP_DEFLATED)

        # the array inner dict key is source file path ,value is target file path
        for root, folders, files in os.walk(test_case_path):
            for sfile in files:
                if root!= attach_path:
                    aFile = os.path.join(root, sfile)
                    zf.write(aFile, os.path.relpath(aFile, test_case_path))

        for m in [[t.task_id ,t.script_name] for t in Upload_TestCase.objects.filter(task_id__iregex=r"^3")]:
            global_script_path = path_combine(upload_path,m[0],m[1])
            zf.write(global_script_path,m[1])

        zf.close()
        response = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % task_id
        response['Content-Length'] = s.tell()

        return response

    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
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

        try:
            update_ini_task(task_id)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

class DeleteTestCaseView(viewsets.ModelViewSet):
    queryset = Upload_TestCase.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [SessionAuthentication,]
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

@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def attach_download_view(request,task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_root = handle_path(path,"upload_files",task_id,"attachment")


    files =[f for f in os.listdir(file_root) if os.path.isfile(os.path.join(file_root,f))]


    file_name = files[0]

    file = open(os.path.join(file_root,file_name), 'rb')
    response = StreamingHttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"'%file_name
    return response

@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def valid_create_script_name_view(request):
    if request.GET:
        task_name = request.GET["task_name"]
        if Upload_TestCase.objects.filter(task_name=task_name).count():
            return JsonResponse({"valid":False})
        else:
            return JsonResponse({"valid": True})

@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def valid_modify_script_name_view(request):
    if request.GET:
        task_name = request.GET["task_name"]
        if Upload_TestCase.objects.filter(task_name=task_name).count() >1:
            return JsonResponse({"valid":False})
        else:
            return JsonResponse({"valid": True})


@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def valid_function_view(request):
    if request.GET:
        script_name = request.GET["script_name"]
        if script_name in [t.script_name for t in Upload_TestCase.objects.filter(task_id__iregex = r"^3") ]:
            return JsonResponse({"valid":False})
        else:
            return JsonResponse({"valid": True})

def remove_upload_file(task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    source_folder = os.path.join(handle_path(path, "upload_files"), task_id)

    # remove  script file
    try:
        shutil.rmtree(source_folder)
    except Exception:
        pass


