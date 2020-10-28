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
from common.handler import *
from common.parser import *

# # Create your views here.
@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def submit_project_view(request):
    if request.method == "POST":

        project_name = request.data.get("project_name")
        token = request.data.get("token")


        # check last project_upload_time the upload_message was True
        instance =  Project_Upload_time.objects.get(project_name=project_name,token=token)
        allow_upload =instance.allow_upload


        if allow_upload == False:
            return JsonResponse({"valid": False, "message": "The project have been modified,please upload new test log."},
                                status=status.HTTP_400_BAD_REQUEST)

        try:
            samba_mount()
        except Exception as e:
            # set had_upload to false
            instance.had_upload =False
            instance.save()
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

                file_list = get_download_file(owner_user,project_name,part_number,station_name,"old")
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
                shutil.rmtree(tmp_path)
                return JsonResponse({"valid": False, "message": re.search(r"\]([\s|\w]+):*",str(e)).group(1).strip()}, status=status.HTTP_417_EXPECTATION_FAILED)

        try:
            os.rename(tmp_path,project_path)
        except Exception as e:
            shutil.rmtree(tmp_path)
            return JsonResponse({"valid": False, "message":re.search(r"\]([\s|\w]+):*",str(e)).group(1).strip()}, status=status.HTTP_417_EXPECTATION_FAILED)

        # update upload time
        instance,created = Project_Upload_time.objects.get_or_create(token=token)

        if created ==False:
            instance.upload_user = User.objects.get(username=request.user)
            instance.time = datetime.datetime.now()
            instance.had_upload = True
            instance.save()


    return  JsonResponse({"valid": True,"message":"Submit successfully!"},status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def copy_part_number_view(request):

    if request.method == "POST":
        project_name = request.data.get("project_name")
        part_number = request.data.get("part_number")
        new_part_number = request.data.get("new_part_number")

        prj_instance = Project.objects.get(project_name=project_name)
        pn_instance = Project_PN.objects.get(project_name=prj_instance,part_number=part_number)

        new_pn = Project_PN.objects.create(project_name=prj_instance, part_number=new_part_number)


        for st in Project_Station.objects.filter(project_pn_id=pn_instance):
            new_st = Project_Station.objects.create(project_pn_id=new_pn, station_name=st.station_name)

            new_task_id = []

            for st_task in Project_task.objects.filter(station_id=st):
                new_st_task = Project_task.objects.create(station_id=new_st, task_id=st_task.task_id,
                                                          task_name=st_task.task_name, timeout=st_task.timeout,
                                                          exit_code=st_task.exit_code,
                                                          retry_count=st_task.retry_count,
                                                          sleep_time=st_task.sleep_time, criteria=st_task.criteria,
                                                          interactive=st_task.interactive, rule=
                                                          st_task.rule, priority=st_task.priority)

                new_task_id.append(new_st_task.id)

                for st_task_arg in Project_task_argument.objects.filter(project_task_id=st_task):
                    Project_task_argument.objects.create(default_value=st_task_arg.default_value,
                                                         argument=st_task_arg.argument, station_id=new_st,
                                                         task_id=st_task.task_id, project_task_id=new_st_task)
            # set testScript ini the testCase order
            task_order = Project_TestScript_order.objects.get(station_name=st, part_number=pn_instance,
                                                              project_name=prj_instance).script_oder.split(" ")
            new_order = set_task_order(task_order, new_task_id)
            Project_TestScript_order.objects.create(station_name=new_st, part_number=new_pn,
                                                    project_name=prj_instance, script_oder=new_order)

            # copy  user_project files
            copy_pn_files(prj_instance.owner_user, project_name, part_number,new_part_number)


    return HttpResponse(status=200)

@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def  copy_project_view(request):
    if request.method == "POST":
        project_name = request.data.get("project_name")
        new_project_name = request.data.get("new_project_name")

        prj_instance = Project.objects.get(project_name=project_name)

        new_prj_instance = Project.objects.create(project_name=new_project_name,
                                                  owner_user=prj_instance.owner_user)

        for pn in Project_PN.objects.filter(project_name=prj_instance):
            new_pn = Project_PN.objects.create(project_name=new_prj_instance,part_number=pn.part_number)

            for st in Project_Station.objects.filter(project_pn_id=pn):
                new_st = Project_Station.objects.create(project_pn_id=new_pn,station_name=st.station_name)

                new_task_id = []

                for st_task in Project_task.objects.filter(station_id=st):
                    new_st_task = Project_task.objects.create(station_id=new_st,task_id=st_task.task_id,task_name=st_task.task_name,timeout=st_task.timeout,exit_code=st_task.exit_code,
                                                              retry_count=st_task.retry_count,sleep_time=st_task.sleep_time,criteria=st_task.criteria,interactive=st_task.interactive,rule=
                                                              st_task.rule,priority=st_task.priority)

                    new_task_id.append(new_st_task.id)

                    for st_task_arg in Project_task_argument.objects.filter(project_task_id=st_task):
                         Project_task_argument.objects.create(default_value=st_task_arg.default_value,argument=st_task_arg.argument,station_id=new_st,task_id=st_task.task_id,project_task_id=new_st_task)

                # set testScript ini the testCase order
                task_order = Project_TestScript_order.objects.get(station_name=st, part_number=pn,
                                                                  project_name=prj_instance).script_oder.split(" ")
                new_order =set_task_order(task_order,new_task_id)
                Project_TestScript_order.objects.create(station_name=new_st,part_number=new_pn,project_name=new_prj_instance,script_oder=new_order)
                # copy  user_project files
                copy_project_files(prj_instance.owner_user, project_name, new_project_name)


        return Response(status=status.HTTP_200_OK)

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
        disable_upload_project(project_name)

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
        disable_upload_project(project_name)

        delete_file(owner_user, project_name, part_number)
        return Response(status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
@permission_classes([IsAdminUser])
def modify_owner_user_view(request):
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
def get_script_sorted_view(request):
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
def valid_log_view(request):
    if request.method == "POST":

        prj = request.data.get("project_name")
        pn = request.data.get("part_number")
        st = request.data.get("station_name")
        token = request.data.get("token")

        if 'file' not in request.FILES:
            return JsonResponse({"valid": False, "message": "Please select the log file."}, status=400)
        file = request.FILES['file']



        try:
            content = (file.read()).decode("utf-8")
        except Exception as e:
            return JsonResponse({"valid": False, "message": "Your test log can't be read."},status=400)

        try:
            check_log(prj,pn,st,content)
        except Exception as e:
            err_msg = str(e)
            return JsonResponse({"valid": False, "message": err_msg}, status=400)

        #token_disable_upload_project(token)

        return JsonResponse({"valid": True, "message": "The log file was passed."})


@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def keep_station_view(request):
    prj = request.data.get("project_name")
    pn = request.data.get("part_number")
    st = request.data.get("station_name")
    token = request.data.get("token")

    try:
       new_version = keep_station(prj,pn,st)
    except Exception as e:
        err_msg = str(e)
        return JsonResponse({"valid": False, "message":err_msg}, status=417)


    # #save the passed project and allow the project to upload
    instance, created = Project_Upload_time.objects.get_or_create(token=token, project_name=Project.objects.get(
        project_name=prj))
    instance.allow_upload = True
    instance.save()

    return JsonResponse({"valid": True, "message": "Keep Station Successfully!","version":new_version})


@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def keep_project_view(request):
    prj = request.data.get("project_name")
    token = request.data.get("token")

    pns = Project_PN.objects.filter(project_name=prj)
    version_data = {}

    for p in pns:
        pn = p.part_number
        sts = Project_Station.objects.filter(project_pn_id=p)
        for s in sts:
            st = s.station_name
            try:
                new_version = keep_station(prj,pn,st)
                version_data[f"{prj}_{pn}_{st}"] = new_version
            except Exception as e:
                err_msg = str(e)
                return JsonResponse({"valid": False, "message": err_msg}, status=417)

    # #save the passed project and allow the project to upload
    instance, created = Project_Upload_time.objects.get_or_create(token=token, project_name=Project.objects.get(
        project_name=prj))
    instance.allow_upload = True
    instance.save()


    return JsonResponse({"valid": True, "message": "Keep Project Successfully!","version_data":version_data})


@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def download_project_view(request,project_name,script_version):
    if request.method == "GET":
        prj = project_name
        user = Project.objects.get(project_name=prj).owner_user.username

        s = BytesIO()
        zf = zipfile.ZipFile(s, "w", compression=zipfile.ZIP_DEFLATED)
        pns = Project_PN.objects.filter(project_name=prj)
        print(pns)

        for p in pns:
            pn = p.part_number
            sts = Project_Station.objects.filter(project_pn_id=p)
            for st in sts:
                st = st.station_name
                files = get_keep_files(user,prj,pn,st,script_version)
                for f in files:

                    thread = threading.Thread(target=lambda zf, f: zf.write(f[0], f[1]), args=(zf, f))
                    thread.start()
                    thread.join()

        zf.close()
        response = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % datetime.datetime.now().strftime(
            '%Y-%m-%d_%H-%M-%S')
        response['Content-Length'] = s.tell()

        return response


@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def upload_view(request):
    if request.method == "POST":
        project_name = request.data.get("project_name")
        part_number = request.data.get("part_number")
        station_name = request.data.get("station_name")
        file = request.FILES['file']

        lines = (file.read()).decode("utf-8")

        try:
            s = upload_script_parser(lines,project_name,part_number,station_name)
            s.convert_script()
            ini_content_map = s.get_ini_content_map()
            task_id = s.get_task_id()

        except Exception as e:
            return JsonResponse({"valid": False, "message": str(e)},
                                status=417)
        return JsonResponse( {"ini_content_map":ini_content_map,"task_id":task_id} , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def download_view(request,project_name,part_number,station_name,script_version):
    if request.method == "GET":
        station_instance = get_station_instacne(project_name, part_number, station_name)
        owner_user =station_instance.project_pn_id.project_name.owner_user.username

        s = BytesIO()
        zf = zipfile.ZipFile(s, "w", compression=zipfile.ZIP_DEFLATED)

        files = get_download_file(owner_user,project_name, part_number, station_name,script_version)
        # the array inner dict key is source file path ,value is target file path
        for f in files:
            thread = threading.Thread(target=lambda zf,f: zf.write(f[0], f[1]), args=(zf, f))
            thread.start()
            thread.join()

        zf.close()
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
        disable_upload_project(project_name)
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def valid_projectt_name_view(request):
    if request.GET:
        project_name = request.GET["project_name"]
        if Project.objects.filter(project_name=project_name).count():
            return JsonResponse({"valid":False})
        else:
            return JsonResponse({"valid": True})

@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def valid_part_number_view(request):
    if request.POST:
        project_name = request.POST["project_name"]
        part_number = request.POST["part_number"]

        if Project_PN.objects.filter(project_name=project_name,part_number=part_number).count():
            return HttpResponse (status=status.HTTP_409_CONFLICT)
        else:
            return HttpResponse (status=status.HTTP_200_OK)

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

def set_task_order(source:list,target:list):

    target_map = {}
    new_order = []
    source_naems = [Project_task.objects.get(id=id).task_name for id in source]

    for id in target:
        target_map[Project_task.objects.get(id=id).task_name] = id

    for name in source_naems:
        new_order.append(str(target_map[name]))

    return " ".join(new_order)

def copy_pn_files(owner_user,prj,source_pn,target_pn):
    root_path = handle_path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "user_project",str(owner_user),prj)

    source_pn_path = handle_path(root_path,source_pn)
    target_pn_path = handle_path(root_path,target_pn)

    copy_files(source_pn_path, target_pn_path)

def copy_project_files(owner_user,source_prj,target_prj):

    root_path = handle_path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "user_project")

    source_path =  handle_path(root_path,str(owner_user),source_prj)
    target_path = handle_path(root_path, str(owner_user),target_prj)

    copy_files(source_path,target_path)

def copy_files(source_path,target_path):
    for dirPath, dirNames, files in os.walk(source_path):

        for file in files:
            source_file = os.path.join(dirPath,file)
            target_file = source_file.replace(source_path,target_path)
            file_root = os.path.dirname(target_file)

            if os.path.exists(file_root) ==False:
                os.makedirs(file_root)
            shutil.copyfile(source_file,target_file)


def check_log(post_prj, post_pn, post_st,content):
    try:
        st_instance = get_station_instacne(post_prj, post_pn, post_st)
    except Exception as e:
        raise Exception("Your station not existed.")

    prj_task_instance = Project_task.objects.filter(station_id=st_instance)

    task_map = {p.task_id_id: p.task_name for p in prj_task_instance}
    if not task_map:
        raise Exception("Your project station was empty.")

    order_instance = Project_TestScript_order.objects.filter(station_name=st_instance)
    if not order_instance:
        raise Exception("Your project station was be created finish.")

    db_order = [int(id) for id in order_instance.first().script_oder.split(" ")]

    # lines = file.read()

    st_reg = re.compile("Station Name.*(PCBA_FT\d{1}|ASSY_PCBA\d+|ASSY_FT\d+|ASSY_OBA_FT\d+)")
    result_reg = re.compile(r"Test Result.+\[(.+)\].+(fail|pass)", re.IGNORECASE)
    id_reg = re.compile('Test case Id.+(\d{6})')
    log_ids = []

    st_groups = [g for g in re.split("\*{2,}", content) if g]

    if len(st_groups) < 2:
        raise Exception("Get station information had error.")

    st = st_reg.findall(st_groups[0])

    if post_st not in st:
        raise Exception("Your station name does not match the database.")

    task_groups = [g for g in re.split("End -+", st_groups[1]) if g]

    for tg in task_groups:
        id_match = id_reg.search(tg)
        if id_match:
            id = id_match.group(1)
        else:
            id = ""
        if id:
            log_ids.append(id)

        for task_name, result in (result_reg.findall(tg)):
            # check had fail result.
            if result == "Fail":
                raise Exception(f"Your task id [{id}] was failed.")

            # check test case id
            if id not in list(task_map.keys()):
                raise Exception(f"Your test case id [{id}] was not on this station.")

            # check test case name
            if task_name not in list(task_map.values()):
                raise Exception(f"Your test case name [{task_name}] was not on this station.")

    # compare order
    log_task_order = []
    for log_id in log_ids:
        for p in prj_task_instance:
            if log_id == p.task_id_id:
                log_task_order.append(p.id)
    if log_task_order != db_order:
        raise Exception("Your test case id does not match the database")


def get_ini_version(version):
    if not version:
        final_version = "1.0.0"
    else:
        cut_ver = [int(v) for v in re.split("\.", version)]
        if (cut_ver[-1] < 99):
            cut_ver[-1] = cut_ver[-1] + 1

        else:
            cut_ver[-1] = 0
            cut_ver[1] = cut_ver[1] + 1

        if cut_ver[1] > 99:
            cut_ver[1] = 0
            cut_ver[0] = cut_ver[0] + 1
        final_version = ".".join([str(v) for v in cut_ver])

    return final_version

def keep_station(prj, pn, st):
    station_instance = get_station_instacne(prj, pn, st)
    owner_user = station_instance.project_pn_id.project_name.owner_user.username
    path =  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target_path = handle_path(path, "user_project", owner_user, prj, pn, st,"keep")

    prj_struct = f"[{prj}/{pn}/{st}]"

    script_path = []

    try:
        shutil.rmtree(target_path, ignore_errors=True)
        files = get_download_file(owner_user, prj, pn, st,"all")
        for f in files:
            dest = path_combine(target_path,f[1])
            path = os.path.dirname(dest)
            if  not os.path.exists(path):
                os.makedirs(path)

            source = f[0]
            target = path_combine(target_path,f[1])

            # update testScript version will re-new it.
            if ("testScript.ini" in os.path.basename(source) ):
                script_path.append([source,target])

            shutil.copy2(source,target)

    except Exception as e:
       raise Exception (f"There is an error in the saving {prj_struct} station file.")


    old_version = station_instance.version
    new_version  =  get_ini_version(old_version)
    station_instance.version = new_version
    station_instance.save()
    update_ini_version(prj,pn,st)

    try:
        #if updated version will re-copy testScript.ini to keep folder
        for s in script_path:
            shutil.copy2(s[0], s[1])
    except Exception as e:
        raise Exception(f"There is an error in keeping {prj_struct} testScript.ini file.")

    return new_version