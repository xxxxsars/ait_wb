from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, Http404, HttpResponseBadRequest
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import redirect
from django.http import HttpResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, RemoteUserAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import random
import string
import zipfile
import json
import shutil
import collections
import multiprocessing
from multiprocessing import Pool
from datetime import datetime
from common.handler import *
from common.limit import set_parameter_arg, set_parameter_other, task_id_reg
from project.forms import *
from project.models import *
from project.restful.views import delete_file






@login_required(login_url="/usr/login")
def log_confirm_view(request, project_name):
    is_project = True

    token = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(30))

    project_structure = []

    p = Project.objects.get(project_name=project_name)
    allow_download = Project_Upload_time.objects.filter(project_name = project_name).exists()


    project_dict = {"project_id": 'prj_%d' % 0, "project_name": p.project_name,
                    "owner_user": p.owner_user.username, "date": p.time,"allow_download":allow_download}
    pn_list = []

    pn_object = Project_PN.objects.filter(project_name=project_name)
    if pn_object.exists():
        for pn_id, pn in enumerate(pn_object):
            pn_dict = model_to_dict(pn)
            pn_dict["pn_id"] = "prj_%d_pn_%d" % (0, pn_id,)
            pn_list.append(pn_dict)
            st_list = []

            st_object = Project_Station.objects.filter(project_pn_id=pn)
            if st_object.exists():
                for st_id, st in enumerate(st_object):
                    st_dict = model_to_dict(st)
                    st_list.append(st_dict)

            pn_dict["st_list"] = st_list

    project_dict["pn_list"] = pn_list
    project_structure.append(project_dict)

    return render(request, "log_confirm.html", locals())


@login_required(login_url="/user/login/")
def list_project_view(request):
    is_project = True

    username = request.user.username
    user_list = [u.username for u in User.objects.all()]
    if request.user.is_staff:
        datas = Project.objects.all()

    else:
        user_instance = User.objects.get(username=username)
        datas = Project.objects.filter(owner_user=user_instance)

    project_structure = []
    for prj_id, p in enumerate(datas):
        project_name = p.project_name
        allow_confirm_log = False
        upload_date = "Not Uploaded"

        filter_instances = [instance for instance in Project_Upload_time.objects.filter(project_name=p) if
                            instance.had_upload]
        if len(filter_instances) > 0:
            upload_date = filter_instances[-1].time



        project_dict = {"project_id": 'prj_%d' % prj_id, "project_name": p.project_name,
                        "owner_user": p.owner_user.username, "date": p.time, "upload_date": upload_date,"allow_upload":Project_Upload_time.objects.filter(project_name=p,allow_upload=True).exists()}

        pn_list = []

        pn_object = Project_PN.objects.filter(project_name=project_name)
        if pn_object.exists():
            for pn_id, pn in enumerate(pn_object):
                pn_dict = model_to_dict(pn)
                pn_dict["pn_id"] = "prj_%d_pn_%d" % (prj_id, pn_id,)
                pn_list.append(pn_dict)
                st_list = []

                st_object = Project_Station.objects.filter(project_pn_id=pn)
                if st_object.exists():
                    for st_id, st in enumerate(st_object):
                        st_dict = model_to_dict(st)

                        # get station task list from order table and  project_task table
                        task_order_instances = Project_TestScript_order.objects.filter(project_name=p, part_number=pn,
                                                                                       station_name=st)
                        if task_order_instances.exists():
                            task_order_list = (task_order_instances[0].script_oder).split(" ")
                            task_list = [str(p.id) for p in Project_task.objects.filter(station_id=st)]
                            # check order and current project task list have any difference
                            ini_not_saved = len(([i for i in task_list + task_order_list if
                                                  i not in task_list or i not in task_order_list])) > 0

                            if ini_not_saved:
                                st_dict["download"] = False
                                allow_confirm_log = False
                            else:
                                st_dict["download"] = True
                                allow_confirm_log = True
                        else:
                            st_dict["download"] = False
                            allow_confirm_log = False

                        st_list.append(st_dict)

                pn_dict["st_list"] = st_list

        project_dict["pn_list"] = pn_list
        project_dict["allow_confirm_log"] = allow_confirm_log
        project_structure.append(project_dict)

    return render(request, "project_list.html", locals())


@login_required(login_url="/user/login")
def create_project_view(request):
    is_project = True

    if request.POST:
        # project_create
        c = CreateProjectForm(request.POST)
        user_name = request.user.username
        if c.is_valid() and valid_user(user_name):
            datas = dict(request.POST)
            project_name = request.POST['project_name']
            part_number = list(filter(None, request.POST.getlist("part_number")))

            # check post data is valid
            if len([item for item, count in dict(collections.Counter(part_number)).items() if count > 1]) > 0:
                errors = "Your PartNumber had some has some repetition."
                return render(request, "project_modify.html", locals())

            r = input_part_station
            if len([e for e in part_number if r.search(e) == None]) > 0:
                errors = "Your PartNumber not match the PartNumber rules."
                return render(request, "project_create.html", locals())

            # if not modify will be check the project had repeat on db
            if "is_modify" not in request.POST:
                if Project.objects.filter(project_name=project_name).count():
                    errors = "Your Project Name cannot be repeated.Please modify your project name."
                    return render(request, "project_create.html", locals())

            user_instance = User.objects.get(username=user_name)

            # if project was existed ,not create it
            if not (Project.objects.filter(project_name=project_name, owner_user=user_instance).exists()):
                project_instance = Project.objects.create(project_name=project_name, owner_user=user_instance)
                for pn in part_number:
                    pn_instance = Project_PN.objects.create(part_number=pn, project_name=project_instance)

            else:
                project_instance = Project.objects.get(project_name=project_name, owner_user=user_instance)
                project_pns = [p.part_number for p in Project_PN.objects.filter(project_name=project_instance)]

                # add new part number
                for post_pn in part_number:
                    if post_pn not in project_pns:
                        pn_instance = Project_PN.objects.create(part_number=post_pn, project_name=project_instance)

                # if db part number not in post part_number
                # ,it means part number may be modify ,it new will be added ,the old will be removed.
                for pn in project_pns:
                    if pn not in part_number:
                        Project_PN.objects.get(part_number=pn, project_name=project_instance).delete()
                        delete_file(user_name, project_name, pn)

            susessful = "Create [ %s ] was successfully! " % project_name
            create_project_folder(user_name, project_name, part_number)
            return render(request, "project_create.html", locals())

        else:
            datas = dict(request.POST)
            return render(request, "project_create.html", locals())
    else:

        c = CreateProjectForm()

    return render(request, "project_create.html", locals())


@login_required(login_url="/user/login")
def modify_project_view(request, project_name, message=None):
    is_project = True
    c = CreateProjectForm()

    # if project_name not existed ,wiil return 404
    if Project.objects.filter(project_name=project_name).exists() == False:
        return Http404

    username = Project.objects.get(project_name=project_name).owner_user.username
    pn_list = Project_PN.objects.filter(project_name=project_name)

    # handle the redirct by modify project name
    if message != None and request.method == "GET":
        susessful = message

    if request.POST:
        datas = dict(request.POST)
        # project_create
        c = CreateProjectForm(request.POST)

        user_name = request.user.username
        if c.is_valid() and valid_user(user_name):
            datas = dict(request.POST)

            post_project_name = request.POST['project_name']
            post_part_numbers = list(filter(None, request.POST.getlist("part_number")))

            # check post data is valid
            if len([item for item, count in dict(collections.Counter(post_part_numbers)).items() if count > 1]) > 0:
                errors = "Your PartNumber had some has some repetition."
                return render(request, "project_modify.html", locals())

            r = input_part_station
            if len([e for e in post_part_numbers if r.search(e) == None]) > 0:
                errors = "Your PartNumber not match the PartNumber rules."
                return render(request, "project_modify.html", locals())

            # if project_name had been modify will redirect to the new page
            if post_project_name != project_name:
                if Project.objects.filter(project_name=post_project_name).count():
                    errors = "Your Project Name cannot be repeated.Please modify your project name."
                    return render(request, "project_create.html", locals())

                user_instance = User.objects.get(username=user_name)
                modify_project_name(project_name, post_project_name)

                # no matter project modify should handle PartNumber
                modify_part_number(post_project_name, post_part_numbers)
                message = "Modify Project successfully!"
                disable_upload_project(project_name)

                return redirect("/project/modify_project/%s/%s" % (post_project_name, message))
            # no matter project modify should handle PartNumber
            modify_part_number(post_project_name, post_part_numbers)
            susessful = "Modify Project successfully!"
            disable_upload_project(project_name)
            return render(request, "project_modify.html", locals())

        else:
            datas = dict(request.POST)
            return render(request, "project_modify.html", locals())

    return render(request, "project_modify.html", locals())


@login_required(login_url='/usr/login')
def set_station_view(request, project_name):
    is_project = True
    username = Project.objects.get(project_name=project_name).owner_user.username
    # check project is valid
    if not request.user.is_staff:
        project_list = [prj[0] for prj in
                        Project.objects.filter(owner_user=User.objects.get(username=username)).values_list(
                            "project_name")]

    else:
        project_list = [prj[0] for prj in Project.objects.all().values_list("project_name")]

    if project_name not in project_list or not valid_user(username):
        return Http404

    user_instance = User.objects.get(username=username)

    project_instance = Project.objects.get(owner_user=user_instance, project_name=project_name)
    pn_instances = Project_PN.objects.filter(project_name=project_instance)

    if request.POST:
        db_part_numbers = [p.part_number for p in pn_instances]
        r = input_part_station

        datas = dict(request.POST)
        datas["all_pn"] = db_part_numbers

        # check all station name is matched our rules.
        for pn in db_part_numbers:
            pn_stations = list(filter(None, request.POST.getlist(pn)))
            if len([e for e in pn_stations if r.search(e) == None]) > 0:
                errors = "Your Station Name not match the Station Name rules."
                return render(request, "station_set.html", locals())

        # if all station valid will do...
        for pn_instance in pn_instances:
            post_stations = list(filter(None, request.POST.getlist(pn_instance.part_number)))
            db_stations = [s.station_name for s in Project_Station.objects.filter(project_pn_id=pn_instance)]

            # if post station name not in db will be created
            for post_station in post_stations:
                if post_station not in db_stations:
                    Project_Station.objects.create(station_name=post_station, project_pn_id=pn_instance)

            # if db station not in post station will be delete
            for db_station in db_stations:
                if db_station not in post_stations:
                    Project_Station.objects.get(station_name=db_station, project_pn_id=pn_instance).delete()
                    delete_file(username, project_name, pn_instance.part_number, db_station)

            create_stations_folder(username, project_name, pn_instance.part_number, post_stations)
        susessful = "Save station name was successfully!"

    return render(request, "station_set.html", locals())


@login_required(login_url='/usr/login')
def modify_station_view(request, project_name, part_number):
    is_project = True
    username = Project.objects.get(project_name=project_name).owner_user.username
    # check project is valid
    if not request.user.is_staff:
        project_list = [prj[0] for prj in
                        Project.objects.filter(owner_user=User.objects.get(username=username)).values_list(
                            "project_name")]
    else:
        project_list = [prj[0] for prj in Project.objects.all().values_list("project_name")]

    part_number_list = [pn.part_number for pn in Project_PN.objects.filter(project_name=project_name)]

    if project_name not in project_list or part_number not in part_number_list or not valid_user(username):
        return Http404

    user_instance = User.objects.get(username=username)

    project_instance = Project.objects.get(owner_user=user_instance, project_name=project_name)
    pn_instance = Project_PN.objects.get(project_name=project_instance, part_number=part_number)
    st_list = Project_Station.objects.filter(project_pn_id=pn_instance)

    if request.POST:
        datas = dict(request.POST)
        post_stations = list(filter(None, request.POST.getlist(part_number)))

        # check post data is valid
        if len([item for item, count in dict(collections.Counter(post_stations)).items() if count > 1]) > 0:
            errors = "Your Station had some has some repetition."
            return render(request, "station_modify.html", locals())

        r = input_part_station
        if len([e for e in post_stations if r.search(e) == None]) > 0:
            errors = "Your Station Name not match the Station Name rules."
            return render(request, "station_modify.html", locals())

        modify_station_name(project_name, part_number, post_stations)
        susessful = "Modify Station Name successfully!"
        disable_upload_project(project_name)

    return render(request, "station_modify.html", locals())


@login_required(login_url="/user/login/")
def select_script_view(request, project_name, part_number, station_name):
    is_project = True

    username = Project.objects.get(project_name=project_name).owner_user.username
    testScript_path = [project_name, part_number, station_name]
    station_instance = get_station_instacne(project_name, part_number, station_name)

    datas = get_script_list()


    # if project name not existed ,will show bad requests
    if (Project.objects.filter(project_name=project_name).exists() == False):
        raise SuspiciousOperation("Invalid request!")

    if request.POST:
        token = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(30))

        # render the set_argument page ,it data get from list page
        if "task_ids" in request.POST:
            if request.POST['task_ids'] != "":
                task_ids = (request.POST['task_ids']).split(",")
                save_add_tasks(task_ids, station_instance)
            prj_task_li = get_station_tasks(project_name, part_number, station_name)

            return render(request, "argument.html", locals())

        # handle appende new task
        if "add_task_ids" in request.POST:
            # if had new task_id must save to database
            if request.POST['add_task_ids'] != "":
                add_task_ids = (request.POST['add_task_ids']).split(",")
                # if will save project_task and project_task_argument ,the data get from default value
                save_add_tasks(add_task_ids, station_instance)
            prj_task_li = get_station_tasks(project_name, part_number, station_name)
            return render(request, "argument.html", locals())

        # handle the select new task action
        if "add_task" in request.POST:
            datas = get_script_list()
            posted_ids = (request.POST["add_task"]).split(",")
            save_modify_tasks(request.POST, station_instance, posted_ids)


            return render(request, "script_list.html", locals())

        # handle the "confirm.htnl"  the  conflict file
        if "conflicted" in request.POST:
            # if will pass value to download page
            # the download need task_id to compress the upload task folder file
            not_dedup_task_ids = str(request.POST["not_dedup_task_ids"]).split(",")

            # download need ini_content_map
            ini_content_map = eval(request.POST["ini_content_map"])

            # get confilict_files to tranfer the choose_map for download page
            confilct_files = str(request.POST["conflict_files"]).split(",")
            testScript_order_list = str(request.POST["testScript_order_list"]).split(",")

            # the testScript ini will be save and used the db order save it.
            save_ini_contents(ini_content_map, testScript_order_list, token)

            chose_map = {}
            for cf in confilct_files:
                if len(cf) > 0:
                    chose_map[cf] = request.POST[cf]

            save_task_files(token, username, project_name, part_number, station_name, not_dedup_task_ids, chose_map)

            # if render the dowload confirm page need "not_dedup_task_ids"  "ini_content_map" "confilct_files" "testScript_order_list"
            return render(request, "confirm.html", locals())



        # handle the set_argument submit action ,it will get all tab parameter
        else:
            post_data = dict(request.POST.lists())
            project_infos = get_project_infos(post_data)

            not_dedup_task_ids = list(
                set([re.search(r"(\w+)_\d+", prj_id).group(1) for prj_id in (post_data["all_task"][0]).split(",")]))

            # if on "confirm page" will save testScript ordering and return order list
            testScript_order_list = [info["project_task_id"] for info in project_infos]
            save_testScript_order(project_name, part_number, station_name, [], False)

            try:
                ini_content_map = gen_ini_contents(project_infos)
            except Exception as e:
                return HttpResponseBadRequest(
                    content=str(e))

            # if  will save and change to confirm page (not matter file confilicted )
            save_modify_tasks(request.POST, station_instance, not_dedup_task_ids)

            # if ajax call will check conflict file
            if 'ajax_saved' in request.POST:
                # check conflict files
                cf = conflict_files(not_dedup_task_ids)

                if len(cf.keys()) != 0:
                    conflict_tmp_path = path_combine(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                     "user_project", "cf_%s.json" % request.POST["conflict_token"])
                    with open(conflict_tmp_path, 'w') as f:
                        json.dump(cf, f)
                    return HttpResponseBadRequest(
                        content='You have some conflicting files. Please click "Next" to proceed.')


            # if submit only check confilct json had existed.
            else:
                conflict_token = request.POST["conflict_token"]
                conflict_tmp_path = path_combine(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                 "user_project", "cf_%s.json" % conflict_token)

                if os.path.exists(conflict_tmp_path):
                    f = open(conflict_tmp_path, 'r')
                    cf = json.loads(f.read())
                    cf_tasks = get_conflict_tasks(cf)
                    err_message = "You have some conflicting files.Please select the file to be compressed into TestCase zip."
                    f.close()
                    # remove tmp file
                    os.remove(conflict_tmp_path)
                    return render(request, "confirm.html", locals())

                # if not conflicted will save ,it had conflicted will change the page to the conflicted page
                save_ini_contents(ini_content_map, testScript_order_list, token)
                save_task_files(token, username, project_name, part_number, station_name, not_dedup_task_ids)

                return render(request, "confirm.html", locals())

    return render(request, "script_list.html", locals())


@login_required(login_url="/user/login/")
def modify_script_view(request, project_name, part_number, station_name):
    is_project = True
    is_modify = True

    username = Project.objects.get(project_name=project_name).owner_user.username
    testScript_path = [project_name, part_number, station_name]
    station_instance = get_station_instacne(project_name, part_number, station_name)
    projetc_task_instances = Project_task.objects.filter(station_id=station_instance)

    # handle query station task query action
    if request.method == "GET":
        conflict_token = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(30))
        prj_task_li = get_station_tasks(project_name, part_number, station_name)
        return render(request, "argument.html", locals())


    elif request.method == "POST":
        token = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(30))

        # handle append new task
        if "add_task_ids" in request.POST:
            # if had new task_id must save to database
            if request.POST['add_task_ids'] != "":
                add_task_ids = (request.POST['add_task_ids']).split(",")
                # if will save project_task and project_task_argument ,the data get from default value
                new_prj_task_ids = save_add_tasks(add_task_ids, station_instance)
            prj_task_li = get_station_tasks(project_name, part_number, station_name)
            disable_upload_project(project_name)
            return render(request, "argument.html", locals())

        # handle the select new task action
        if "add_task" in request.POST:
            datas = get_script_list()
            posted_ids = (request.POST["add_task"]).split(",")

            # if the original argument page paramter had been change will be modify it.
            save_modify_tasks(request.POST, station_instance, posted_ids)
            return render(request, "script_list.html", locals())

        # handle the "confirm.htnl"  the  conflict file
        if "conflicted" in request.POST:
            # if will pass value to download page
            # the download need task_id to compress the upload task folder file
            not_dedup_task_ids = str(request.POST["not_dedup_task_ids"]).split(",")

            # download need ini_content_map
            ini_content_map = eval(request.POST["ini_content_map"])

            # get confilict_files to tranfer the choose_map for download page
            confilct_files = str(request.POST["conflict_files"]).split(",")
            testScript_order_list = str(request.POST["testScript_order_list"]).split(",")

            chose_map = {}
            for cf in confilct_files:
                if len(cf) > 0:
                    chose_map[cf] = request.POST[cf]

            # the testScript ini will be save and used the db order save it.
            save_ini_contents(ini_content_map, testScript_order_list, token)

            save_task_files(token, username, project_name, part_number, station_name, not_dedup_task_ids, chose_map)

            return render(request, "confirm.html", locals())

        else:
            post_data = dict(request.POST.lists())
            if "new_prj_task_ids" in request.POST:
                new_prj_task_ids = (request.POST.get('new_prj_task_ids')).split(" ")

            project_infos = get_project_infos(post_data)

            not_dedup_task_ids = list(
                set([re.search(r"(\w+)_\d+", prj_id).group(1) for prj_id in (post_data["all_task"][0]).split(",")]))

            try:
                ini_content_map = gen_ini_contents(project_infos)
            except Exception as e:
                return HttpResponseBadRequest(
                    content=str(e))

            # if  will save and change to confirm page (not matter file conflicted )
            save_modify_tasks(request.POST, station_instance, not_dedup_task_ids)

            # if on "confirm page" will save testScript ordering and return order list
            sorted_list = [info["project_task_id"] for info in project_infos]
            testScript_order_list = save_testScript_order(project_name, part_number, station_name, sorted_list, False)
            disable_upload_project(project_name)

            # if ajax call will check conflict file
            if 'ajax_saved' in request.POST:
                # check conflict files
                cf = conflict_files(not_dedup_task_ids)

                if len(cf.keys()) != 0:
                    conflict_tmp_path = path_combine(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                     "user_project", "cf_%s.json" % request.POST["conflict_token"])
                    with open(conflict_tmp_path, 'w') as f:
                        json.dump(cf, f)
                    return HttpResponseBadRequest(
                        content='You have some conflicting files. Please click "Next" to proceed.')


            # if submit only check confilct json had existed.
            else:
                conflict_token = request.POST["conflict_token"]
                conflict_tmp_path = path_combine(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                 "user_project", "cf_%s.json" % conflict_token)

                if os.path.exists(conflict_tmp_path):
                    f = open(conflict_tmp_path, 'r')
                    cf = json.loads(f.read())
                    cf_tasks = get_conflict_tasks(cf)
                    err_message = "You have some conflicting files.Please select the file to be compressed into TestCase zip."
                    f.close()
                    # remove tmp file
                    os.remove(conflict_tmp_path)
                    return render(request, "confirm.html", locals())

                # if not conflicted will save ,it had conflicted will change the page to the conflicted page
                save_ini_contents(ini_content_map, testScript_order_list, token)
                save_task_files(token, username, project_name, part_number, station_name, not_dedup_task_ids)

                return render(request, "confirm.html", locals())

    return render(request, "argument.html", locals())


@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def result_ini_view(request, project_name, part_number, station_name,):
    is_project = True # show "back to list"
    is_modify = True #upload script not need order
    token = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(30))  #if modifiied ,it was the tmp.ini name
    testScript_path = [project_name, part_number, station_name]

    ini_content_map = {}
    not_dedup_task_ids = []
    testScript_order_list = []

    ini_reg = re.compile(r"^ini_content_map\[(\d+)\]")
    task_reg = re.compile(r"^task_id\[(\d+)\]")

    for k,v in (request.POST.dict()).items():
        ini_match = ini_reg.search(k)
        task_match =task_reg.search(k)

        if ini_match:
            ini_id = ini_match.group(1)
            testScript_order_list.append(ini_id)
            ini_content_map[ini_id] = v

        if task_match:
            task_id = v
            not_dedup_task_ids.append(task_id)

    return render(request, "confirm.html", locals())


@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def save_ini_view(request, token):

    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if request.POST:
        # if testScript not been resorted will only provide file download service
        if 'save_ini' in request.POST:
            # save new testScript.ini
            with open(os.path.join(handle_path(path, "user_project"), "%s.ini" % token), "w") as f:
                # add space line for every testCase
                new_content = ""
                for line in (request.POST["ini_content"].split("\n")):
                    if re.search(r"criteria=.*", line):
                        new_content += line + "\n\n"
                    else:
                        new_content += line + '\n'

                f.write(new_content)

            # # save those file to owner user folder
            username = request.user.username
            path = request.POST.getlist("path[]")
            project_name = path[0]
            part_number = path[1]
            station_name = path[2]

            # save new ini
            save_token_ini(token, username, project_name, part_number, station_name)
            # save the new order to db
            sorted_list = request.POST.getlist("sroted_list[]")
            save_testScript_order(project_name, part_number, station_name, sorted_list, True)
            disable_upload_project(project_name)

        return HttpResponse(status=200)


def save_token_ini(token, username, project_name, part_number, station_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest_path = handle_path(path, "user_project", username, project_name, part_number, station_name)
    ini_path = os.path.join(handle_path(path, "user_project"), "%s.ini" % token)
    shutil.copy2(ini_path, os.path.join(dest_path, "testScript.ini"))
    os.remove(ini_path)
    update_ini_version(project_name, part_number, station_name)


def save_task_files(token, username, project_name, part_number, station_name, task_list, chose_files=None):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    dest_path = handle_path(path, "user_project", username, project_name, part_number, station_name)
    keep_path = handle_path(path, "user_project", username, project_name, part_number, station_name,"keep")

    for root, dirs, files in os.walk(dest_path):
        if keep_path not in root :
            for f in files:
                print(os.path.join(root, f))
                os.unlink(os.path.join(root, f))
            for d in dirs:
                if keep_path not in os.path.join(root, d):
                    shutil.rmtree(os.path.join(root, d))


    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    chose_files_path = []
    if chose_files != None:
        for file, task_id in chose_files.items():
            chose_files_path.append(os.path.join(handle_path(path, "upload_files", task_id), file))

    # create task files information json file
    json_data = {}
    with open(os.path.join(dest_path, "file_info.json"), "w") as f:
        json_data["task_list"] = task_list
        if chose_files != None:
            json_data["chose_file"] = chose_files
        json.dump(json_data, f)

    # add ini
    save_token_ini(token, username, project_name, part_number, station_name)


def task_files(task_list):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "upload_files")

    task_files = {}
    for task_id in task_list:
        file_path = os.path.join(root_path, task_id)
        file_list = []
        for root, folders, files in os.walk(file_path):

            for sfile in files:
                aFile = os.path.join(root, sfile)
                file_list.append(os.path.relpath(aFile, file_path))

        task_files[task_id] = file_list

    return task_files


def get_md5_map(file, result_map):
    result_map[file] = md5(file)
    return result_map


def conflict_files(task_list):
    root_path = handle_path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'upload_files')
    dedup = []
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_map = task_files(task_list)

    pool = Pool()
    result = []
    md5_map = {}

    for k, fs in file_map.items():
        for f in fs:
            if re.search("attachment.*", f) == None:
                file_path = path_combine(path, 'upload_files', k, f)
                tmp_map = {}
                result.append(pool.apply_async(get_md5_map, args=(file_path, tmp_map,)))

    pool.close()
    pool.join()

    for i in result:
        for f, md5 in i.get().items():
            md5_map[f] = md5

    new_files = {}
    for path, md5 in md5_map.items():

        if platform.system() == "Windows":
            match = re.search(r'upload_files\\(\w+)\\(.+)', path)
        else:
            match = re.search(r'upload_files/(\w+)/(.+)', path)

        if match:
            file = match.group(2)

            if file in new_files.keys():
                # check md5 ,if  same will append to the deduplicate list
                if md5 != new_files[file]:
                    dedup.append(file)
            else:
                new_files[file] = md5

    dedup_map = {}
    for k, fs in file_map.items():
        file_list = []
        for f in fs:
            if f in dedup:
                file_list.append(f)
        if len(file_list) != 0:
            dedup_map[k] = file_list

    return dedup_map


def get_conflict_tasks(conflict_dict):
    # get conflict file
    conflict_files = []
    for k, files in conflict_dict.items():
        for f in files:
            if f in conflict_files:
                pass
            else:
                conflict_files.append(f)

    # get confilct task map by conflict file
    conflict_task = {}
    for cf in conflict_files:
        tasks = []
        for k, files in conflict_dict.items():
            if cf in files:
                tasks.append(k)
        conflict_task[cf] = tasks
    return conflict_task


def get_station_instacne(project, part_number, station):
    project_instance = Project.objects.get(project_name=project)
    pn_instance = Project_PN.objects.get(project_name=project_instance, part_number=part_number)
    station_instance = Project_Station.objects.get(project_pn_id=pn_instance, station_name=station)
    return station_instance


def get_script_name(task_id):
    task_instance = Upload_TestCase.objects.get(task_id=task_id)
    return task_instance.script_name


def get_project_infos(post):
    new_prj_task_ids = []
    project_task_ids = (post["all_task"][0]).split(",")
    new_prj_obj = (post.get("new_prj_task_ids"))
    if new_prj_obj:
        new_prj_task_ids = new_prj_obj[0].split(" ")

    project_infos = []
    for prj_id in project_task_ids:
        tmp_prj_info = {}
        tmp_arg_value_map = {}

        id_reg = re.search(r"(.+)_(\d+)", prj_id)
        task_id = id_reg.group(1)
        project_task_id = id_reg.group(2)
        tmp_prj_info["task_id"] = task_id
        tmp_prj_info["script_name"] = get_script_name(task_id)
        tmp_prj_info["project_task_id"] = project_task_id

        if project_task_id in new_prj_task_ids:
            tmp_prj_info["new_task"] = True
        else:
            tmp_prj_info["new_task"] = False

        for k, v in post.items():
            prj_id_reg = re.search(r"(.*)_%s$" % prj_id, k)
            if prj_id_reg:
                prj_match = prj_id_reg.group(1)
                prj_arg_reg = re.search(r'arg_(\w+)', prj_match)
                if prj_arg_reg:
                    tmp_arg_value_map[prj_arg_reg.group(1)] = v[0]
                else:
                    tmp_prj_info[prj_match] = v[0]
        tmp_prj_info["args"] = sorted_arg_value(task_id, tmp_arg_value_map)

        project_infos.append(tmp_prj_info)

    return project_infos


def get_station_tasks(project_name, part_number, station_name):
    part_number_instance = Project_PN.objects.get(project_name=project_name, part_number=part_number)
    station_instance = Project_Station.objects.get(station_name=station_name, project_pn_id=part_number_instance)
    projetc_task_instances = Project_task.objects.filter(station_id=station_instance)

    station_task_ids = [p.task_id.task_id for p in projetc_task_instances]
    # remove same task id
    task_ids = []
    for id in station_task_ids:
        if id not in task_ids:
            task_ids.append(id)

    prj_task_li = []

    existed_task_id = {}
    for id in task_ids:
        for prj_task in projetc_task_instances.filter(task_id=id):
            task_map = model_to_dict(prj_task)
            prj_arg_li = []

            # if had same task name will add serial number
            task_id = task_map["task_id"]
            project_task_name = task_map["task_name"]

            # if the task name had be repeated and not append serial number will add serial number
            if task_id in list(existed_task_id.values()) and project_task_name in list(existed_task_id.keys()):
                task_map["task_name"] = task_map["task_name"] + " %d" % list(existed_task_id.values()).count(task_id)
            existed_task_id[task_map["task_name"]] = task_id

            for arg in Project_task_argument.objects.filter(project_task_id=prj_task):
                prj_arg_li.append({'id': arg.id, 'default_value': arg.default_value, 'argument': arg.argument.argument,
                                   'task_id': arg.task_id.task_id, "description": arg.argument.description})

            task_map["args"] = prj_arg_li

            task_instance = Upload_TestCase.objects.get(task_id=task_map["task_id"])

            arg_instances = Arguments.objects.filter(task_id=task_map["task_id"])

            usage_content = ""
            for arg in arg_instances:
                if re.search("^-\w{1}", arg.default_value) == None:
                    usage_content += "-%s\n&nbsp;&nbsp;&nbsp;&nbsp;%s\n" % (arg.argument, arg.description)

            task_map["project_description"] = "Sample:\n%s\n\nUsage:\n%s" % (task_instance.sample, usage_content)

            prj_task_li.append(task_map)

    sorted_prj_task_ids = sorted([info["id"] for info in prj_task_li])

    sorted_prj_task_li = []

    for sid in sorted_prj_task_ids:
        for info in prj_task_li:
            if info["id"] == sid:
                sorted_prj_task_li.append(info)

    return sorted_prj_task_li


def gen_ini_contents(project_infos):
    new_prj_task_ids = []

    ini_map = {}
    for prj_info in (project_infos):
        project_task_id = prj_info["project_task_id"]
        task_id = prj_info["task_id"]

        interactive = "AUTO"
        if prj_info['interactive'] != 'auto':
            interactive = "INTERACTIVE"

        title = "[0_%s_%s_%s]\n" % (interactive, task_id, prj_info["task_name"])
        script_path = r'cmd=TestScriptRes\\%s' % prj_info["script_name"]
        arg_str = " ".join([arg for arg in prj_info["args"]])
        args = prj_info["args"]
        remove_args = []
        # if arg was empty will not add to content
        for i, arg in enumerate(args):
            if re.search("^\-\w+$", arg):
                try:
                    next_arg = args[i + 1]
                except Exception as e:
                    raise Exception("Your argument had some error ,please modify it.")
                if next_arg == "":
                    remove_args.append(arg)
                    remove_args.append(next_arg)
        if len(args) > 0:
            for r_arg in remove_args:
                args.remove(r_arg)
        arg_str = " ".join([arg for arg in args])

        # if was interactive item the content will be emptied
        if task_id[1] != "6":
            content = "%s %s;%s;%s;%s;%s\ncriteria=%s\n" % (
                script_path, arg_str, prj_info["timeout"], prj_info["exitcode"], prj_info["retry"], prj_info["sleep"],
                prj_info["criteria"])
        else:
            content = "criteria=%s\n" % prj_info["criteria"]

        if prj_info['interactive'] != 'auto':
            rule = "%s=%s" % ((prj_info['interactive']).upper(), prj_info['rule'])

            if prj_info['priority'] == "interactive":
                ini_map[project_task_id] = title + rule + "\n" + content
            else:
                ini_map[project_task_id] = title + content + rule

        elif prj_info['interactive'] == 'auto':
            ini_map[project_task_id] = title + content

        if prj_info["new_task"]:
            new_prj_task_ids.append(prj_info["project_task_id"])
    ini_map["new_prj_task_ids"] = new_prj_task_ids

    return ini_map


# save int will be save before the download page ,it use token to the file name
def save_ini_contents(ini_map, ini_order_list, token):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ini_content = ""

    for id in ini_order_list:
        ini_content += ini_map[id] + "\n"

    # save ini
    with open(os.path.join(handle_path(path, "user_project"), "%s.ini" % token), "w") as f:
        f.write(ini_content)


# if will return the new project_task id list
def save_add_tasks(add_task_ids, station_instance):
    prj_task_ids = []
    for task_id in add_task_ids:
        task_instance = Upload_TestCase.objects.get(task_id=task_id)
        prj_task_instance = Project_task.objects.create(station_id=station_instance, task_id=task_instance,
                                                        task_name=task_instance.task_name, timeout=10,
                                                        exit_code="exitCode", retry_count=5, sleep_time=0,
                                                        criteria="PASS")

        prj_task_ids.append(str(prj_task_instance.id))

        for arg in Arguments.objects.filter(task_id=task_instance):
            Project_task_argument.objects.create(default_value=arg.default_value, argument=arg,
                                                 station_id_id=station_instance.id, task_id=task_instance,
                                                 project_task_id=prj_task_instance)
    return " ".join(prj_task_ids)


# add the new testCase on the project and handle the repeated test case add the serial number
def save_modify_tasks(post, station_instance, posted_ids):
    projetc_task_instances = Project_task.objects.filter(station_id=station_instance)

    task_ids = []
    for id in posted_ids:
        if id not in task_ids:
            task_ids.append(id)
    for id in task_ids:
        for prj_task in projetc_task_instances.filter(task_id=id):
            prj_task.task_name = post["task_name_%s_%s" % (id, prj_task.id)]
            prj_task.timeout = post["timeout_%s_%s" % (id, prj_task.id)]
            prj_task.exit_code = post["exitcode_%s_%s" % (id, prj_task.id)]
            prj_task.retry_count = post["retry_%s_%s" % (id, prj_task.id)]
            prj_task.sleep_time = post["sleep_%s_%s" % (id, prj_task.id)]
            prj_task.criteria = post["criteria_%s_%s" % (id, prj_task.id)]

            prj_task.interactive = post["interactive_%s_%s" % (id, prj_task.id)]

            if prj_task.interactive != "auto":
                prj_task.rule = post["rule_%s_%s" % (id, prj_task.id)]
                prj_task.priority = post["priority_%s_%s" % (id, prj_task.id)]
            else:
                prj_task.rule = ""
                prj_task.priority = ""

            prj_task.save()
            for arg in Project_task_argument.objects.filter(project_task_id=prj_task):
                argument_name = arg.argument.argument
                arg.default_value = post["arg_%s_%s_%s" % (argument_name, id, arg.project_task_id.id)]
                arg.save()


def save_testScript_order(project_name, part_number, station_name, sorted_list, force_change_sortted):
    project_instance = Project.objects.get(project_name=project_name)
    part_number_instance = Project_PN.objects.get(project_name=project_name, part_number=part_number)
    station_instance = Project_Station.objects.get(station_name=station_name, project_pn_id=part_number_instance)

    order_instance = Project_TestScript_order.objects.filter(project_name=project_instance,
                                                             part_number=part_number_instance,
                                                             station_name=station_instance)

    # handle the "modify" task order
    if order_instance.exists():
        if len(order_instance) > 1:
            raise ValueError("Your testScript oder was repeated")
        else:
            if force_change_sortted:

                order_content = " ".join(sorted_list)
                order_instance[0].script_oder = order_content
                order_instance[0].save()
                return sorted_list

            else:
                # that will not change the original db order
                db_order = (order_instance[0].script_oder).split(' ')
                # means the task had been add
                for id in sorted_list:
                    if id not in db_order:
                        db_order.append(id)
                # means the task had been remove
                for id in db_order:
                    if id not in sorted_list:
                        db_order.remove(id)

                order_content = " ".join(db_order)
                order_instance[0].script_oder = order_content
                order_instance[0].save()

                return db_order

    #  handle "create" task order
    else:
        order_content = " ".join(sorted_list)
        Project_TestScript_order.objects.update_or_create(script_oder=order_content, project_name=project_instance,
                                                          part_number=part_number_instance,
                                                          station_name=station_instance)
    return sorted_list


def modify_station_name(project_name, part_number, post_st_list):
    project_instance = Project.objects.get(project_name=project_name)
    user_name = project_instance.owner_user.username
    pn_instance = Project_PN.objects.get(project_name=project_instance, part_number=part_number)
    stations = [s.station_name for s in Project_Station.objects.filter(project_pn_id=pn_instance)]

    if len(post_st_list) >= len(stations):
        for i, st in enumerate(stations):
            # if not match ,it was be modified
            if st != post_st_list[i]:
                st_instance = Project_Station.objects.get(project_pn_id=pn_instance, station_name=st)
                st_instance.station_name = post_st_list[i]
                st_instance.save()

                modify_station_folder(user_name, project_name, part_number, st, post_st_list[i])

        for post_st in post_st_list[len(stations):]:
            Project_Station.objects.create(project_pn_id=pn_instance, station_name=post_st)
            create_single_station_folder(user_name, project_name, part_number, post_st)
    else:
        raise ValueError("Your station name had error.")


def modify_part_number(project_name, post_pn_list):
    project_instance = Project.objects.get(project_name=project_name)
    user_name = project_instance.owner_user.username
    project_pns = [p.part_number for p in Project_PN.objects.filter(project_name=project_instance)]

    if len(post_pn_list) >= len(project_pns):
        for i, pn in enumerate(project_pns):
            if pn != post_pn_list[i]:
                # if not match ,it was modify
                if post_pn_list[i] != pn:
                    pn_instance = Project_PN.objects.get(project_name=project_instance, part_number=pn)
                    pn_instance.part_number = post_pn_list[i]
                    pn_instance.save()
                    modify_pn_folder(user_name, project_name, pn, post_pn_list[i])
        # if not in db will create new one
        for post_pn in post_pn_list[len(project_pns):]:
            Project_PN.objects.create(project_name=project_instance, part_number=post_pn)
            create_pn_folder(user_name, project_name, post_pn)

    else:
        raise ValueError("Your part number had error.")


def modify_project_name(old_name, new_name):
    project_instance = Project.objects.get(project_name=old_name)
    pn_instances = Project_PN.objects.filter(project_name=project_instance)
    user_name = project_instance.owner_user.username

    project_instance.project_name = new_name

    project_instance.save()

    for pn in pn_instances:
        pn.project_name = project_instance
        pn.save()

    Project.objects.get(project_name=old_name).delete()

    modify_project_folder(user_name, new_name, old_name)


def sorted_arg_value(task_id, value_map):
    task_instance = Upload_TestCase.objects.get(task_id=task_id)
    db_args = [a.argument for a in Arguments.objects.filter(task_id=task_instance)]
    sort_values = []

    for arg in db_args:
        sort_values.append(value_map[arg])

    return sort_values


def valid_user(username):
    if User.objects.filter(username=username).exists():
        return True
    else:
        return False
