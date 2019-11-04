from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, Http404
from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import redirect

import random
import string
from datetime import datetime
import zipfile
import json
import collections

from common.limit import set_parameter_arg, set_parameter_other, task_id_reg
from common.common import *
from project.forms import *
from project.models import *
from project.restful.views import delete_file
from test_script.list.views import no_attach_tasks


@login_required(login_url="/user/login/")
def list_project(request):
    is_project = True
    username = request.user.username

    # clean not selected task project
    # for p in Project.objects.all():
    #
    #     pn_instance = Project_PN.objects.filter(project_name_id=p)
    #
    #     if len(pn_instance) ==0:
    #         p.delete()
    #
    #
    #     # if len(Project_task.objects.filter(project_name=p)) == 0:
    #     #     p.delete()
    #
    if request.user.is_staff:
        datas = Project.objects.all()


    else:
        user_instance = User.objects.get(username=username)
        datas = Project.objects.filter(owner_user=user_instance)

    project_structure = []
    for prj_id, p in enumerate(datas):
        project_name = p.project_name
        project_dict = {"project_id": 'prj_%d' % prj_id, "project_name": p.project_name,
                        "owner_user": p.owner_user.username, "date": p.time}
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
                        st_list.append(st_dict)

                pn_dict["st_list"] = st_list

        project_dict["pn_list"] = pn_list
        project_structure.append(project_dict)

    return render(request, "project_list.html", locals())


@login_required(login_url="/user/login")
def modify_project(request, project_name,message=None):
    is_project = True
    c = CreateProjectForm()
    user_name = request.user.username
    pn_list = Project_PN.objects.filter(project_name=project_name)


    # handle the redirct by modify project name
    if message !=None and request.method=="GET":
        susessful = message

    if request.POST:
        save_post = True
        print(dict(request.POST))
        # project_create
        c = CreateProjectForm(request.POST)

        user_name = request.user.username
        if c.is_valid() and valid_user(user_name):
            datas = dict(request.POST)

            post_project_name = request.POST['project_name']
            post_part_numbers = list(filter(None, request.POST.getlist("part_number")))

            # check post data is valid
            if len([item for item ,count in  dict(collections.Counter(post_part_numbers)).items() if count >1]) >0:
                errors = "Your PartNumber had some has some repetition."
                return render(request, "project_modify.html", locals())


            r = input_part_station
            if len([e for e in post_part_numbers if r.search(e) == None]) > 0:
                errors = "Your PartNumber not match the PartNumber rules."
                return render(request, "project_modify.html", locals())


            # if project_name had been modify will redirect to the new page
            if post_project_name !=project_name:
                if Project.objects.filter(project_name=post_project_name).count():
                    errors = "Your Project Name cannot be repeated.Please modify your project name."
                    return render(request, "create.html", locals())

                user_instance = User.objects.get(username=user_name)
                modify_project_name(project_name,post_project_name)

                # no matter project modify should handle PartNumber
                modify_part_number(post_project_name, post_part_numbers)
                message = "Modify Project successfully!"
                save_post = False
                return redirect("/project/modify_project/%s/%s"%(post_project_name,message))
            # no matter project modify should handle PartNumber
            modify_part_number(post_project_name, post_part_numbers)
            susessful = "Modify Project successfully!"
            save_post = False
            return render(request, "project_modify.html", locals())
        else:
            datas = dict(request.POST)
            return render(request, "project_modify.html", locals())


    return render(request, "project_modify.html", locals())


@login_required(login_url="/user/login")
def create_project(request):
    is_project = True

    if request.POST:
        # project_create
        c = CreateProjectForm(request.POST)
        user_name = request.user.username
        if c.is_valid() and valid_user(user_name):
            datas = dict(request.POST)
            project_name = request.POST['project_name']
            part_number = list(filter(None, request.POST.getlist("part_number")))

            r = input_part_station
            if len([e for e in part_number if r.search(e) == None]) > 0:
                errors = "Your PartNumber not match the PartNumber rules."
                return render(request, "create.html", locals())

            # if not modify will be check the project had repeat on db
            if "is_modify" not in request.POST:
                if Project.objects.filter(project_name=project_name).count():
                    errors = "Your Project Name cannot be repeated.Please modify your project name."
                    return render(request, "create.html", locals())

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
            return render(request, "create.html", locals())

        else:
            datas = dict(request.POST)
            return render(request, "create.html", locals())
    else:

        c = CreateProjectForm()

    return render(request, "create.html", locals())


@login_required(login_url='/usr/login')
def set_station(request, project_name):
    is_project = True
    username = request.user.username
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
                return render(request, "set_station.html", locals())

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

            create_station_folder(username, project_name, pn_instance.part_number, post_stations)
        susessful = "Save station name was successfully!"

    return render(request, "set_station.html", locals())


@login_required(login_url="/user/login/")
def select_script(request, project_name, part_number, station_name):
    is_project = True
    datas = Upload_TestCase.objects.all()
    no_att_tasks = no_attach_tasks()

    # if project name not existed ,will show bad requests
    if (Project.objects.filter(project_name=project_name).exists() == False):
        raise SuspiciousOperation("Invalid request!")

    if request.POST:
        token = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(30))

        # render the set_argument page ,it data get from list page
        if "task_ids" in request.POST:
            task_ids = (request.POST['task_ids']).split(",")
            arg_dict = {}
            task_dict = {}

            if len(task_ids) != 0:
                for task_id in task_ids:
                    task_info = Upload_TestCase.objects.get(task_id=task_id)
                    args = Arguments.objects.filter(task_id=task_info)
                    arg_dict[task_id] = list(args.values())
                    task_dict[task_id] = task_info.task_name

                arg_json = json.dumps(arg_dict)
                return render(request, "set_argument.html", locals())
            else:
                raise Http404

        ## =====================start confirm page handle============================##

        # handle the "confirm.htnl"  the  conflict file
        if "conflicted" in request.POST:

            # get task_ids and result_dict from not conflict page.
            task_ids = str(request.POST["task_list"]).split(",")
            result_dict = eval(request.POST['result_dict'])

            confilct_files = str(request.POST["conflict_files"]).split(",")
            render_di = eval(request.POST["ini_content"])

            chose_map = {}
            for cf in confilct_files:
                if len(cf) > 0:
                    chose_map[cf] = request.POST[cf]

            return render(request, "confirm.html", locals())

        # handle the set_argument submit action ,it will get all tab parameter
        else:
            task_ids = []
            result_dict = {}

            arg_reg = set_parameter_arg
            other_reg = set_parameter_other

            for k, v in dict(request.POST.lists()).items():
                pd = []

                if arg_reg.match(k):
                    task_id = arg_reg.search(k).group(1)

                    if task_id not in task_ids:
                        task_ids.append(task_id)

                    task_info = Upload_TestCase.objects.get(task_id=task_id)
                    script_name = task_info.script_name
                    task_name = task_info.task_name
                    parmeter = arg_reg.search(k).group(2)
                    argument = v[0]

                    if task_id in result_dict:
                        pd = result_dict[task_id]
                        pd[parmeter] = argument
                    else:
                        result_dict[task_id] = {parmeter: argument,
                                                "script_name": script_name, "task_name": task_name}

            for task_id in task_ids:
                append_dict = result_dict[task_id]
                append_dict["timeout"] = request.POST["timeout_%s" % task_id]
                append_dict["exitcode"] = request.POST["exitcode_%s" % task_id]
                append_dict["retry"] = request.POST["retry_%s" % task_id]
                append_dict["sleep"] = request.POST["sleep_%s" % task_id]
                append_dict["criteria"] = request.POST["criteria_%s" % task_id]
                append_dict["project_name"] = project_name
                append_dict["part_number"] = part_number
                append_dict["station_name"] = station_name

            render_str = ""
            render_di = {}

            for task_id in task_ids:
                render_di[task_id] = gen_ini_str(task_id, result_dict) + "\n"

            # check conflict files
            cf = conflict_files(result_dict)

            if len(cf.keys()) != 0:
                cf_tasks = get_conflict_tasks(cf)
                disable_download = True
                err_message = "You have some conflicting files.Please select the file to be compressed into TestCase zip. "

                return render(request, "confirm.html", locals())

            # if not conflict files will show  confirm page and the project can be downloaded.
            return render(request, "confirm.html", locals())
        ## =====================end confirm page handle============================##

    return render(request, "script_list.html", locals())


'''
@login_required(login_url="/user/login")
def modify_project(request, project_name):
    is_project = True
    is_modify = True

    username = request.user.username

    # check project is valid
    if not request.user.is_staff:
        project_list = [prj[0] for prj in
                        Project.objects.filter(owner_user=User.objects.get(username=username)).values_list(
                            "project_name")]
    else:
        project_list = [prj[0] for prj in Project.objects.all().values_list("project_name")]
    if project_name not in project_list:
        return Http404

    if request.method == "POST":
        token = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(30))

        # handle the "confirm.htnl"  the  conflict file
        if "conflicted" in request.POST:

            # get task_ids and result_dict from not conflict page.
            task_ids = str(request.POST["task_list"]).split(",")
            result_dict = eval(request.POST['result_dict'])

            confilct_files = str(request.POST["conflict_files"]).split(",")
            render_di = eval(request.POST["ini_content"])

            chose_map = {}
            for cf in confilct_files:
                if len(cf) > 0:
                    chose_map[cf] = request.POST[cf]

            return render(request, "confirm.html", locals())


        else:
            task_ids = []
            result_dict = {}

            arg_reg = set_parameter_arg
            other_reg = set_parameter_other

            for k, v in dict(request.POST.lists()).items():
                pd = []

                if arg_reg.match(k):
                    task_id = arg_reg.search(k).group(1)

                    if task_id not in task_ids:
                        task_ids.append(task_id)

                    task_info = Upload_TestCase.objects.get(task_id=task_id)
                    script_name = task_info.script_name
                    task_name = task_info.task_name
                    parmeter = arg_reg.search(k).group(2)
                    argument = v[0]

                    if task_id in result_dict:
                        pd = result_dict[task_id]
                        pd[parmeter] = argument
                    else:
                        result_dict[task_id] = {parmeter: argument,
                                                "script_name": script_name, "task_name": task_name}

            for task_id in task_ids:
                append_dict = result_dict[task_id]
                append_dict["timeout"] = request.POST["timeout_%s" % task_id]
                append_dict["exitcode"] = request.POST["exitcode_%s" % task_id]
                append_dict["retry"] = request.POST["retry_%s" % task_id]
                append_dict["sleep"] = request.POST["sleep_%s" % task_id]
                append_dict["criteria"] = request.POST["criteria_%s" % task_id]
                append_dict["project_name"] = project_name

            render_str = ""
            render_di = {}

            project_owner_user = Project.objects.get(project_name=project_name).owner_user.username
            sotred_ids = sorted_task_ids(project_name, project_owner_user)

            for task_id in sotred_ids:

                render_di[task_id] = gen_ini_str(task_id, result_dict) + "\n"

            # check conflict files
            cf = conflict_files(result_dict)

            if len(cf.keys()) != 0:
                cf_tasks = get_conflict_tasks(cf)
                disable_download = True
                err_message = "You have some conflicting files.Please select the file to be compressed into TestCase zip. "

                return render(request, "confirm.html", locals())


            return render(request, "confirm.html", locals())


    elif request.method == "GET":
        task_ids = [prj.task_id.task_id for prj in Project_task.objects.filter(project_name=project_name)]
        arg_dict = {}
        task_dict = {}

        for task_id in task_ids:
            task_instance = Upload_TestCase.objects.get(task_id=task_id)
            project_instance = Project.objects.get(project_name=project_name)
            args = Project_task_argument.objects.filter(project_name=project_instance).filter(task_id=task_instance)

            arg_dict[task_id] = list(args.values())

            tmp_dict = {"task_name": task_instance.task_name}
            tmp_dict["task_args"] = model_to_dict(Project_task.objects.filter(project_name=project_instance).get(
                task_id=task_instance))

            task_dict[task_id] = tmp_dict

        arg_json = json.dumps(arg_dict)

    return render(request, "set_argument.html", locals())
'''


def download(request, token):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(handle_path(path, "download_folder"), "%s.zip" % token)

    if request.POST:
        # if testScript not been resorted will only provide file download service
        if request.POST['item_moved'] == "False":
            file = open(file_path, 'rb')
            response = StreamingHttpResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="%s.zip"' % datetime.now().strftime(
                '%Y-%m-%d_%H-%M-%S')
            return response

        else:
            post_args = eval(request.POST['result_dict'])
            username = request.user.username
            project_name = ""
            part_number = ""
            station_name = ""
            for task_id, argumes in post_args.items():
                project_name = argumes['project_name']
                part_number = argumes['part_number']
                station_name = argumes['station_name']

            # save ini
            with open(os.path.join(handle_path(path, "download_folder"), "%s.ini" % token), "w") as f:
                f.write(request.POST["ini_content"])

            # compress all file to zip file
            task_list = str(request.POST["task_list"]).split(",")

            if "chose_files" in request.POST:
                chose_map = eval(request.POST["chose_files"])
                conflict_archive_folder(task_list, token, chose_map)
            else:
                archive_folder(task_list, token)

            # provide the download link service
            file = open(file_path, 'rb')
            response = StreamingHttpResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="%s.zip"' % datetime.now().strftime(
                '%Y-%m-%d_%H-%M-%S')

            # save all project parameter to database
            save_project_info(post_args)

            # save those file to owner user folder
            save_project_files(token, username, project_name, part_number, station_name)

            return response

    else:
        return Http404


def archive_folder(task_list, token):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = handle_path(path, "ait_config")
    dest_path = handle_path(path, "download_folder")
    script_path = "TestScriptRes"

    ini_path = os.path.join(dest_path, "%s.ini" % token)

    dest_zip = "%s.zip" % token

    zf = zipfile.ZipFile(os.path.join(dest_path, dest_zip), mode='w')

    compressed_file = []
    for task_id in task_list:
        file_path = handle_path(path, "upload_folder", task_id)

        # add source pyfile
        attach_path = handle_path(file_path, "attachment")
        for root, folders, files in os.walk(file_path):
            for sfile in files:
                # ignore attachment path
                if root != attach_path:
                    if sfile not in compressed_file:
                        aFile = os.path.join(root, sfile)
                        zf.write(aFile, os.path.join(script_path, os.path.relpath(aFile, file_path)))
                        compressed_file.append(sfile)

    # add default configuration
    for root, folders, files in os.walk(config_path):
        for sfile in files:
            aFile = os.path.join(root, sfile)
            zf.write(aFile, os.path.relpath(aFile, config_path))

    # add ini
    zf.write(ini_path, "testScript.ini")

    os.remove(ini_path)

    zf.close()


def conflict_archive_folder(task_list, token, chose_files):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_path = handle_path(path, "ait_config")
    dest_path = handle_path(path, "download_folder")
    script_path = "TestScriptRes"
    file_path = handle_path(path, "upload_folder")

    ini_path = os.path.join(dest_path, "%s.ini" % token)

    dest_zip = "%s.zip" % token

    zf = zipfile.ZipFile(os.path.join(dest_path, dest_zip), mode='w')

    chose_files_path = []
    for file, task in chose_files.items():
        chose_files_path.append(os.path.join(os.path.join(file_path, task), file))

    compressed_file = []
    for task_id in task_list:
        source_file_path = handle_path(file_path, task_id)
        attach_path = handle_path(source_file_path, "attachment")

        # add source pyfile
        for root, folders, files in os.walk(source_file_path):
            for sfile in files:
                # ignore attachment path
                if root != attach_path:
                    aFile = os.path.join(root, sfile)
                    dest_file = os.path.relpath(aFile, source_file_path)

                    if dest_file in list(chose_files.keys()):
                        if aFile in chose_files_path:
                            zf.write(aFile, os.path.join(script_path, dest_file))

                    # if had compress file not compress again
                    elif sfile not in compressed_file:
                        zf.write(aFile, os.path.join(script_path, dest_file))
                        compressed_file.append(sfile)

    # add default configuration
    for root, folders, files in os.walk(config_path):
        for sfile in files:
            aFile = os.path.join(root, sfile)

            zf.write(aFile, os.path.relpath(aFile, config_path))

    # add ini
    zf.write(ini_path, "testScript.ini")

    os.remove(ini_path)
    zf.close()


def gen_ini_str(task_id, argumet_dict):
    di = argumet_dict[task_id]

    task_name = di["task_name"]
    script_name = di["script_name"]

    title = "[0_AUTO_%s_%s]\n" % (task_id, task_name)

    script_path = r'cmd=TestScriptRes\\%s' % script_name
    arg_str = ""
    argumes = Arguments.objects.filter(task_id=task_id)

    for arg in argumes:
        arg_str += " %s" % di[arg.argument]

    content = "%s%s;%s;%s;%s;%s\ncriteria=%s" % (
        script_path, arg_str, di["timeout"], di["exitcode"], di["retry"], di["sleep"], di["criteria"])

    return title + content


def task_files(task_list):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    task_files = {}
    for task_id in task_list:
        if platform.system() == "Windows":
            file_path = path + r'\upload_folder\\' + task_id
        else:
            file_path = path + '/upload_folder/' + task_id

        # add source pyfile
        file_list = []
        for root, folders, files in os.walk(file_path):

            for sfile in files:
                aFile = os.path.join(root, sfile)
                file_list.append(os.path.relpath(aFile, file_path))

        task_files[task_id] = file_list

    return task_files


def conflict_files(result_dict):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    task_list = list(result_dict.keys())

    file_map = task_files(task_list)

    new_files = {}

    dedup = []
    for k, fs in file_map.items():

        if platform.system() == "Windows":
            file_path = path + r'\upload_folder\\' + k
        else:
            file_path = path + '/upload_folder/' + k

        for f in fs:
            if f in new_files.keys():
                # check md5 ,if  same will append to the deduplicate list
                if md5(os.path.join(file_path, f)) != new_files[f]:
                    dedup.append(f)
            else:
                new_files[f] = md5(os.path.join(file_path, f))

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


def sorted_task_ids(project_name, user_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # path =os.path.dirname(os.path.abspath(__file__))
    if platform.system() == "Windows":
        root_path = path + r'\download_folder\\' + user_name


    else:
        root_path = path + '/download_folder/' + user_name

    ini_path = os.path.join(os.path.join(root_path, project_name), "testScript.ini")

    sorted_ids = []

    r = re.compile("^\[.*_(%s\d{2})_.*\]$" % task_id_reg)
    with open(ini_path, "r") as f:
        for line in f.readlines():
            matched = r.search(line)
            if matched:
                sorted_ids.append(matched.group(1))

    return sorted_ids


def save_project_info(datas):
    for task_id, argumes in datas.items():
        project_name = argumes['project_name']
        part_number = argumes["part_number"]
        station_name = argumes["station_name"]

        task_instance = Upload_TestCase.objects.get(task_id=task_id)
        station_instance = get_station_instacne(project_name, part_number, station_name)
        #
        p, created = Project_task.objects.get_or_create(station_id=station_instance,
                                                        task_id=task_instance)
        # whatever it created ,all need modify it value.
        p.criteria = argumes['criteria']
        p.exit_code = argumes["exitcode"]
        p.retry_count = argumes["retry"]
        p.sleep_time = argumes['sleep']
        p.timeout = argumes['timeout']
        p.save()

        db_args = Arguments.objects.filter(task_id=task_id)
        for arg in db_args:
            a, created = Project_task_argument.objects.get_or_create(argument=arg.argument,
                                                                     station_id=station_instance,
                                                                     task_id=task_instance)
            # whatever it created ,all need modify it value.
            a.default_value = argumes[arg.argument]
            a.save()


def save_project_files(token, username, project_name, part_number, station_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    source_path = handle_path(path, "download_folder")

    source_zip = os.path.join(source_path, "%s.zip" % token)
    dest_path = handle_path(source_path, username, project_name, part_number, station_name)

    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    else:
        for root, dirs, files in os.walk(dest_path):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(dest_path)


def create_project_folder(username, project_name, part_numbers):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name)
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    for part_number in part_numbers:
        part_number_path = os.path.join(root_path, part_number)
        if not os.path.exists(part_number_path):
            os.makedirs(part_number_path)


def create_station_folder(username, project_name, part_number, stations):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name, part_number)
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    for station in stations:
        station_path = os.path.join(root_path, station)
        if not os.path.exists(station_path):
            os.makedirs(station_path)


def valid_user(username):
    if User.objects.filter(username=username).exists():
        return True
    else:
        return False
