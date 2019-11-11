from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import os
import shutil
import platform
import collections

from test_script.update.forms import *
from test_script.upload.forms import *
from common.limit import input_argument, valid_default_value
from common.handler import handle_path
from project.models import *


@login_required(login_url="/user/login/")
def modify_index(request, task_id):
    is_script = True

    u = UpdateFileForm()

    # let js can't dynamic add argument column
    a = ArgumentForm()

    task_info = Upload_TestCase.objects.get(task_id=task_id)
    args = Arguments.objects.filter(task_id=task_info)
    render_value = True

    if request.POST:
        u = UpdateFileForm(request.POST, request.FILES)

        if u.is_valid():
            id = request.POST["task_id"]
            task_name = request.POST["task_name"]
            task_descript = request.POST["task_description"]
            script_name = request.POST["script_name"]
            sample = request.POST["sample"]

            if "file" in request.FILES:
                try:
                    handle_update_file(request.FILES['file'], id)
                except Exception as e:
                    error_message = "Upload file is no valid zip file."
                    return render(request, "script_modify.html", locals())

            up = Upload_TestCase.objects.get(task_id=task_id)

            if 'attachment' in request.FILES:
                handle_update_attachment(request.FILES['attachment'], id)
                up.existed_attachment =True
            else:
                up.existed_attachment = False

            # handle post task information
            up.task_name = task_name
            up.script_name = script_name
            up.description = task_descript
            up.sample = sample

            # handle modify argument
            arg_infos = Arguments.objects.filter(task_id=task_info)

            # check ths post data valid
            posted_args = []
            for arg in arg_infos:
                post_arg = request.POST["arg_%s" % arg.argument]
                post_value = request.POST["value_%s" % arg.argument]

                # handle render post value
                if input_argument.search(post_arg) != None:
                    error_message = "Your arguments only allow number, letter and underline."
                    return render(request, "script_modify.html", locals())

                if post_arg in posted_args:
                    error_message = "Your parameters only allow unique values."
                    return render(request, "script_modify.html", locals())
                posted_args.append(post_arg)

                if valid_default_value(post_value) == False:
                    error_message = "Your default value does not match the rule."
                    return render(request, "script_modify.html", locals())

            # vaild data will be modify
            for arg in arg_infos:
                post_arg = request.POST["arg_%s" % arg.argument]
                post_descript = request.POST["des_%s" % arg.argument]
                post_value = request.POST["value_%s" % arg.argument]

                arg.argument = post_arg
                arg.description = post_descript
                arg.default_value = post_value
                arg.save()

            # handle new argument

            # check if the parameter is a duplicate
            db_args = [i["argument"] for i in arg_infos.values("argument")]

            if "argument" and "description" and "default_value" in request.POST:
                descripts = request.POST.getlist("description")
                arguments = request.POST.getlist("argument")
                values = request.POST.getlist("default_value")

                for arg in arguments:
                    if input_argument.search(arg) != None:
                        error_message = "Your arguments only allow number, letter and underline."
                        return render(request, "script_modify.html", locals())

                # check new argument not deplicate
                if len([item for item, count in collections.Counter(arguments).items() if count > 1]) > 0:
                    error_message = "Your parameters only allow unique values."
                    return render(request, "script_modify.html", locals())

                for i, e in enumerate(arguments):
                    argument = arguments[i]
                    description = descripts[i]
                    value = values[i]

                    if argument in db_args:
                        error_message = "Your parameters only allow unique values."
                        return render(request, "script_modify.html", locals())

                    a = Arguments.objects.create(argument=argument, description=description, default_value=value,
                                                 task_id=up)
                    # if had new arg the project argument must be update
                    for prj_task in Project_task.objects.filter(task_id=up):
                        if not Project_task_argument.objects.filter(project_task_id=prj_task, argument=a).exists():
                            Project_task_argument.objects.create(default_value=a.default_value, argument=a, task_id=up,
                                                                 station_id=prj_task.station_id,
                                                                 project_task_id=prj_task)

            # arguments create finish will save the change
            up.save()

            susessful = "Update Test Case ID: [ %s ] was successfully!" % task_id
            # update update value
            task_info = Upload_TestCase.objects.get(task_id=task_id)
            args = Arguments.objects.filter(task_id=task_info)

        else:
            # if not valid display post data
            render_value = False

    return render(request, "script_modify.html", locals())


def handle_update_attachment(f, task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    save_path = handle_path(path, "upload_folder", task_id, "attachment")

    try:
        shutil.rmtree(save_path)
    except Exception:
        pass

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    with open(os.path.join(save_path, f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


# handle_update_file will remove all unzip folder
def handle_update_file(f, task_id):
    if input_zip_file_name.search(str(f.name)) == None:
        raise Exception("Upload file is no valid zip file.")

    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_zip = os.path.join(handle_path(path, "upload_folder"), f.name)
    unzip_path = os.path.join(handle_path(path, "upload_folder"), task_id)

    with open(source_zip, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # check vaild zip file
    try:
        zip_file = zipfile.ZipFile(source_zip)
        ret = zip_file.testzip()

        if ret is not None:
            raise Exception("not valid zip")
        zip_file.close()
    except Exception:
        os.remove(source_zip)
        raise Exception("Upload file is no valid zip file.")

    # remove old script file
    for file in os.listdir(unzip_path):
        if file != "attachment":
            file_path = os.path.join(unzip_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)

    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(unzip_path)

    os.remove(source_zip)
