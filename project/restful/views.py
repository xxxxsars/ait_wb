from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, RemoteUserAuthentication
from rest_framework.permissions import IsAuthenticated

from django.http import HttpResponse
from django.http.response import JsonResponse
from django.http import StreamingHttpResponse

import threading
import shutil,zipfile,os,subprocess,re,platform,string,random,time
from io import StringIO,BytesIO

from FactoryWeb.settings import *
from project.restful.serializer import *
from project.models import *
from common.handler import handle_path,get_download_file,path_combine,samba_mount


# # Create your views here.


@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def submit_project(request):
    if request.method == "POST":
        project_name = request.data.get("project_name")
        try:
            samba_mount()
        except Exception as e:

            return JsonResponse (  {"valid": False,"message":"Connection failed."},status=status.HTTP_408_REQUEST_TIMEOUT)



        p = ""
        if (platform.system() == "Darwin"):
            p = OSX_MOUNT_PATH
        elif platform.system() == "Windows":
            p = WIN_MOUNT_PATH

        project_instance = Project.objects.get(project_name=project_name)
        owner_user = project_instance.owner_user.username

        tmp_folder_name = "".join([ random.choice(string.ascii_letters+string.digits)  for _ in range(30)])
        for pn in Project_PN.objects.filter(project_name=project_instance):
            for st in Project_Station.objects.filter(project_pn_id=pn):
                part_number = pn.part_number
                station_name = st.station_name

                file_list = get_download_file(owner_user,project_name,part_number,station_name)
                for source_path,target in file_list:
                    target_path = path_combine(p,tmp_folder_name,part_number,station_name)

                    if not os.path.exists(target_path):
                        os.makedirs(target_path)

                    target_full_path,_ = os.path.split(os.path.join(target_path,target))
                    if not os.path.exists(target_full_path):
                        os.makedirs(target_full_path)
                    shutil.copy2(source_path,target_full_path)



        # remove old project folder and change tmp name
        tmp_path = path_combine(p, tmp_folder_name)
        project_path = path_combine(p, project_name+"_test")
        if os.path.exists(project_path):
            try:
                shutil.rmtree(project_path)
            except Exception as e:
                print(tmp_path)
                shutil.rmtree(tmp_path)
                return JsonResponse({"valid": False, "message": re.search(r"\]([\s|\w]+):*",str(e)).group(1).strip()}, status=status.HTTP_417_EXPECTATION_FAILED)

        try:
            os.rename(tmp_path,project_path)
        except Exception as e:
            print(tmp_path)
            shutil.rmtree(tmp_path)
            return JsonResponse({"valid": False, "message":re.search(r"\]([\s|\w]+):*",str(e)).group(1).strip()}, status=status.HTTP_417_EXPECTATION_FAILED)

        # Add upload time
        p = Project.objects.get(project_name=project_name)
        Project_Upload_time.objects.create(project_name=p,time=datetime.datetime.now())


    return  JsonResponse({"valid": True,"message":"Submit successfully!"},status=status.HTTP_200_OK)










@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
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
@authentication_classes((SessionAuthentication,))
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
@authentication_classes((SessionAuthentication,))
@permission_classes([IsAdminUser])
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



class DeleteProjectView(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = [SessionAuthentication ]
    http_method_names = ['delete']


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project_name = instance.project_name
        owner_user = instance.owner_user.username

        delete_file(owner_user, project_name)
        # print(request.user)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
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






@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def valid_testSCript(request):
    if request.method == "POST":

        project_name = request.data.get("project_name")
        part_number = request.data.get("part_number")
        station_name = request.data.get("station_name")

        if 'file' not in request.FILES:
            return JsonResponse({"valid": False, "message": "Please select the log file."}, status=400)
        file = request.FILES['file']

        task_id_line_inedx = []
        task_names = []
        task_ids = []
        compare_task_name = []

        station_instance = get_station_instacne(project_name,part_number,station_name)


        lines = file.readlines()
        valid_reg = re.compile(r"\[([\w|\s]+) -.+\]-+>\s(\w+).+$")
        station_regex = re.compile("\*.+Station Name\s*\?*(\w+)")
        test_id_regex = re.compile('Test case Id:\s*\[(\d{6})\]')

        station_match_count=0
        for index,byte_line in enumerate(lines):
            line = byte_line.decode("utf-8")
            # check station name
            station_match = (station_regex.search(line))
            if station_match:
                station_match_count+=1
                log_station = station_match.group(1)
                if log_station != station_name:
                    return JsonResponse({"valid": False,"message":"The log file station name not compared."},status=400)



            # check log the all task was passed
            matched = valid_reg.search(line)
            if matched:
                if matched.group(2) =="PASS":
                    # add pass task name to list
                    task_names.append((matched.group(1).strip()))
                    task_id_line_inedx.append(index+1)

                else:
                    return JsonResponse({"valid": False,"message":"The testCase '%s' was failed."%matched.group(1).strip()},status=400)

            if index in task_id_line_inedx:
                # add pass task id to list
                test_id_match = test_id_regex.search(line)
                if test_id_match:
                        task_ids.append(test_id_match.group(1))

        if station_match_count <=0:
            return JsonResponse({"valid": False, "message": "Can't find log station name."},status=400)


        # check testScript order
        task_id_map = {p.id: p.task_name for p in Project_task.objects.filter(station_id=station_instance)}
        sort_task_name_id = Project_TestScript_order.objects.get(station_name=station_instance).script_oder.split(" ")

        for id in sort_task_name_id:
            compare_task_name.append((task_id_map[int(id)]).strip())

        # check testCase id
        compare_task_id = [instance.task_id.task_id  for instance in
                           Project_task.objects.filter(station_id=station_instance)]

        # check task name
        if task_names == compare_task_name :

            #check task id
            sort_compare_task_id = [int(i) for i in compare_task_id]
            sort_task_ids = [int(i) for i in task_ids]

            sort_compare_task_id.sort()
            sort_task_ids.sort()
            if sort_compare_task_id == sort_task_ids:
                return JsonResponse({"valid": True,"message":"The log file was passed."})
        else:

            return JsonResponse({"valid": False,"message":"Please re-download this testScript and test it aging."},status=400)





@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def download(request,project_name,part_number,station_name):
    if request.method == "GET":
        station_instance = get_station_instacne(project_name, part_number, station_name)
        owner_user =station_instance.project_pn_id.project_name.owner_user.username

        s = BytesIO()
        zf = zipfile.ZipFile(s, "w", compression=zipfile.ZIP_DEFLATED)

        files = get_download_file(owner_user,project_name, part_number, station_name)
        # the array inner dict key is source file path ,value is target file path
        for f in files:
            thread = threading.Thread(target=lambda zf,f: zf.write(f[0], f[1]), args=(zf, f))
            thread.start()
            thread.join()

        response = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        response['Content-Length'] = s.tell()

        return response
    return Response(status=status.HTTP_400_BAD_REQUEST)

class DeleteProjectTaskView(viewsets.ModelViewSet):
    queryset = Project_task.objects.all()
    serializer_class = ProjectTaskSerializer
    authentication_classes = [SessionAuthentication, ]
    permission_classes = [IsAuthenticated]
    http_method_names = ['delete']

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


@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def valid_projectt_name(request):
    if request.GET:
        project_name = request.GET["project_name"]
        if Project.objects.filter(project_name=project_name).count():
            return JsonResponse({"valid":False})
        else:
            return JsonResponse({"valid": True})






def change_project(project_name,old_username, new_username):
    path = handle_path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "user_project")

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
    rm_path = handle_path(path, "user_project", username, *args)
    shutil.rmtree(os.path.join(path, rm_path))


def get_station_instacne(project, part_number, station):
    project_instance = Project.objects.get(project_name=project)
    pn_instance = Project_PN.objects.get(project_name=project_instance, part_number=part_number)
    station_instance = Project_Station.objects.get(project_pn_id=pn_instance, station_name=station)
    return station_instance





