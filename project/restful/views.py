from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication,RemoteUserAuthentication

from project.restful.serializer import *
from project.models import *

import os, platform, shutil

from common.common import handle_path

# # Create your views here.



@api_view(["POST"])
@authentication_classes((BasicAuthentication,))
def DeleteProjectStationView(request):
    if request.method == "POST":
        project_name = request.data.get("project_name")
        part_number = request.data.get("part_number")
        station_name = request.data.get("station_name")

        if project_name ==None or project_name ==None or station_name ==None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        owner_user = Project.objects.get(project_name=project_name).owner_user.username
        pn_instance = Project_PN.objects.get(project_name=project_name,part_number=part_number)
        station_instance = Project_Station.objects.filter(station_name=station_name,project_pn_id=pn_instance)
        if station_instance.exists() ==False:
            return Response(status=status.HTTP_400_BAD_REQUEST)


        station_instance.delete()

        delete_file(owner_user,project_name,part_number,station_name)
        #
        # delete_pn_file(owner_user,project_name,part_number)
        return Response(status=status.HTTP_200_OK)




@api_view(["POST"])
@authentication_classes((BasicAuthentication,))
def DeleteProjectPNView(request):
    if request.method == "POST":

        project_name = request.data.get("project_name")
        part_number = request.data.get("part_number")

        if project_name ==None or project_name ==None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        pn_instance = Project_PN.objects.filter(project_name=project_name,part_number=part_number)
        owner_user = Project.objects.filter(project_name=project_name).owner_user.username
        if pn_instance.exists() ==False:
            return Response(status=status.HTTP_400_BAD_REQUEST)


        pn_instance.delete()

        delete_file(owner_user,project_name,part_number)
        return Response(status=status.HTTP_200_OK)




class DeleteProjectView(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [BasicAuthentication,]
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




def delete_file(username,*args):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    rm_path = handle_path(path,"download_folder",username,*args)
    shutil.rmtree(os.path.join(path,rm_path))
