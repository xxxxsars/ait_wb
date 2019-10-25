from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from project.restful.serializer import  *
from project.models import *


import os,platform,shutil
# Create your views here.


class DeleteProjectView(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [ BasicAuthentication]
    http_method_names = ['delete']
    # permission_classes = (IsAdminUser,)





    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        project_name = instance.project_name
        owner_user = instance.owner_user.username

        delet_project_file(owner_user,project_name)
        # print(request.user)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)




def delet_project_file(username,project_name):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if platform.system() == "Windows":
        project_path = path + r"\download_folder\\"+username

    else:
        project_path = path + "/download_folder/"+username


    shutil.rmtree(os.path.join(project_path,project_name))