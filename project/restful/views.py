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
# class DeleteProjectPNView(viewsets.ModelViewSet):
#     queryset = Project_PN.objects.all()
#     serializer_class = ProjectPNSerializer
#     authentication_classes = [BasicAuthentication]
#     # http_method_names = ['delete']
#
#     # permission_classes = (IsAdminUser,)
#
#     def destroy(self, request, *args, **kwargs):
#
#         print(request,args,kwargs)
#         instance = self.get_object()
#
#         print(instance.project_name)
#         # project_name = instance.project_name
#         # owner_user = instance.owner_user.username
#
#         # print(request.user)
#         # self.perform_destroy(instance)
#         return Response(status=status.HTTP_204_NO_CONTENT)






@api_view(["POST"])
@authentication_classes((BasicAuthentication,))
def DeleteProjectPNView(request):
    if request.method == "POST":

        project_name = request.data.get("project_name")
        part_number = request.data.get("part_number")

        if project_name ==None or project_name ==None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        pn_instance = Project_PN.objects.filter(project_name=project_name,part_number=part_number)
        owner_user = Project.objects.get(project_name=project_name).owner_user.username
        if pn_instance.exists() ==False:
            return Response(status=status.HTTP_400_BAD_REQUEST)


        pn_instance.delete()

        delete_pn_file(owner_user,project_name,part_number)
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

        delete_project_file(owner_user, project_name)
        # print(request.user)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



def delete_pn_file(username, project_name,part_number):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pn_path = handle_path(path,"download_folder",username,project_name,part_number)
    shutil.rmtree(pn_path)


def delete_project_file(username, project_name):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    project_path = handle_path(path,"download_folder",username)
    shutil.rmtree(os.path.join(project_path, project_name))
