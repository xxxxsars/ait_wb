from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, RemoteUserAuthentication

from django.http import HttpResponse
from django.http.response import JsonResponse
from project.restful.serializer import *
from project.models import *

import os, platform, shutil,zipfile
from io import StringIO,BytesIO

from common.handler import handle_path
from django.http import StreamingHttpResponse
from project.models import *

# # Create your views here.


@api_view(["POST"])
@authentication_classes((BasicAuthentication,))
def DeleteProjectStationView(request):
    if request.method == "POST":
        project_name = request.data.get("project_name")
        part_number = request.data.get("part_number")
        station_name = request.data.get("station_name")

        if project_name == None or project_name == None or station_name == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        owner_user = Project.objects.get(project_name=project_name).owner_user.username
        pn_instance = Project_PN.objects.get(project_name=project_name, part_number=part_number)
        station_instance = Project_Station.objects.filter(station_name=station_name, project_pn_id=pn_instance)
        if station_instance.exists() == False:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        station_instance.delete()

        delete_file(owner_user, project_name, part_number, station_name)
        #
        # delete_pn_file(owner_user,project_name,part_number)
        return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes((BasicAuthentication,))
def DeleteProjectPNView(request):
    if request.method == "POST":

        project_name = request.data.get("project_name")
        part_number = request.data.get("part_number")

        if project_name == None or project_name == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        pn_instance = Project_PN.objects.filter(project_name=project_name, part_number=part_number)
        owner_user = Project.objects.get(project_name=project_name).owner_user.username
        if pn_instance.exists() == False:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        pn_instance.delete()

        delete_file(owner_user, project_name, part_number)
        return Response(status=status.HTTP_200_OK)



@api_view(["POST"])
@authentication_classes((BasicAuthentication,))
def ModifyOwnerUser(request):
    if request.method == "POST":
        project_name = request.data.get("project_name")
        username = request.data.get("username")

        project_instances = Project.objects.filter(project_name= project_name)

        if project_instances.exists():
            prj_instance = project_instances[0]
            old_username = prj_instance.owner_user.username

            new_user_instance = User.objects.get(username=username)

            change_project(project_name,old_username,username)
            prj_instance.owner_user = new_user_instance
            prj_instance.save()
            return Response(status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes((BasicAuthentication,))
def GetScriptSorted(request):
    if request.method == "POST":
        project_name = request.data.get("project_name")
        part_number = request.data.get("part_number")
        station_name = request.data.get("station_name")

        project_instance = Project.objects.get(project_name=project_name)
        pn_instance = Project_PN.objects.get(project_name=project_instance, part_number=part_number)
        station_instance = Project_Station.objects.get(project_pn_id=pn_instance, station_name=station_name)

        script_oder = Project_TestScript_order.objects.get(project_name_id=project_name, part_number=pn_instance,
                                                           station_name=station_instance).script_oder

        data = {"script_oder": script_oder.split(" ")}
        return JsonResponse(data)


@api_view(["GET"])
@authentication_classes((BasicAuthentication,))
def download(request,project_name,part_number,station_name):
    if request.method == "GET":
        station_instance = get_station_instacne(project_name, part_number, station_name)
        owner_user = station_instance.project_pn_id.project_name.owner_user
        path = handle_path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                           "download_folder", str(owner_user), project_name, part_number, station_name)


        s = BytesIO()
        zf = zipfile.ZipFile(s, "w",compression=zipfile.ZIP_DEFLATED)

        # the array inner dict key is source file path ,value is target file path
        for root, folders, files in os.walk(path):
            for sfile in files:
                aFile = os.path.join(root, sfile)
                zf.write(aFile, os.path.relpath(aFile, path))
        zf.close()
        response = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        response['Content-Length'] = s.tell()

        return response
    return Response(status=status.HTTP_400_BAD_REQUEST)

class DeleteProjectTaskView(viewsets.ModelViewSet):
    queryset = Project_task.objects.all()
    serializer_class = ProjectTaskSerializer
    authentication_classes = [BasicAuthentication, ]

    # http_method_names = ['delete']

    # permission_classes = (IsAdminUser,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # remove the script oder on project_task_order table
        owner_user = instance.station_id.project_pn_id.project_name.owner_user
        project_name = instance.station_id.project_pn_id.project_name_id
        part_number = instance.station_id.project_pn_id
        station_name = instance.station_id
        project_task_id = instance.id

        prj_script_instances = Project_TestScript_order.objects.filter(project_name=project_name,
                                                                       part_number=part_number,
                                                                       station_name=station_name)

        if prj_script_instances.exists():
            project_order_instance = prj_script_instances[0]
            script_oder_list = (project_order_instance.script_oder).split(" ")
            for prj_id in script_oder_list:
                # if delete project_task_id in project_task_order will remove it from order table
                if str(project_task_id) == prj_id:
                    script_oder_list.remove(prj_id)
            project_order_instance.script_oder = " ".join(script_oder_list)
            project_order_instance.save()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteProjectView(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [BasicAuthentication, ]
    http_method_names = ['delete']

    # permission_classes = (IsAdminUser,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project_name = instance.project_name
        owner_user = instance.owner_user.username

        delete_file(owner_user, project_name)
        # print(request.user)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


def change_project(project_name,old_username, new_username):
    path = handle_path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "download_folder")

    old_path = handle_path(path, old_username, project_name)
    new_path = handle_path(path, new_username)

    # Delete project with the same name has been forced to move
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    # if the project was existed on the user folder will remove it.
    elif os.path.exists(os.path.join(new_path,project_name)):
        shutil.rmtree(os.path.join(new_path,project_name))

    shutil.move(old_path, new_path)



def delete_file(username, *args):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    rm_path = handle_path(path, "download_folder", username, *args)
    shutil.rmtree(os.path.join(path, rm_path))


def get_station_instacne(project, part_number, station):
    project_instance = Project.objects.get(project_name=project)
    pn_instance = Project_PN.objects.get(project_name=project_instance, part_number=part_number)
    station_instance = Project_Station.objects.get(project_pn_id=pn_instance, station_name=station)
    return station_instance
