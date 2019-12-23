from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, RemoteUserAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

import os
import shutil
import platform
import collections

from test_script.update.forms import *
from test_script.upload.forms import *
from common.limit import input_argument, valid_default_value
from common.handler import handle_path, get_attach_name, get_modify_time
from project.models import *

@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def update_API(request):
    error_messages = []
    if request.POST:
        task_id = request.POST["task_id"]
        task_name = request.POST["task_name"]
        task_descript = request.POST["task_description"]
        script_name = request.POST["script_name"]
        sample = request.POST["sample"]

        if "file" in request.FILES:
            try:
                handle_update_file(request.FILES['file'], task_id)
            except Exception as e:
                error_messages.append("Upload file is no valid zip file.")

        task_info = Upload_TestCase.objects.get(task_id=task_id)

        if 'attachment' in request.FILES:
            handle_update_attachment(request.FILES['attachment'], task_id)
            task_info.existed_attachment = True
            attach_name = request.FILES["attachment"].name

        # handle post task information
        task_info.task_name = task_name
        task_info.script_name = script_name
        task_info.description = task_descript
        task_info.sample = sample
        task_info.time = datetime.datetime.now()
        task_info.save()

        db_args = [a.argument for a in Arguments.objects.filter(task_id=task_info)]

        descripts = request.POST.getlist("description")
        arguments = request.POST.getlist("argument")
        values = request.POST.getlist("default_value")


        # if post argument more than database argument will create it.
        if len(arguments) > len(db_args):
            index = len(db_args)
            new_args =arguments[index::]

            for i,arg in  enumerate(new_args):
                argument = arguments[index+i]
                description = descripts[index+i]
                value = values[index+i]
                a = Arguments.objects.create(argument=argument, description=description, default_value=value,
                                             task_id=task_info)
                # if had new arg the project argument must be update
                for prj_task in Project_task.objects.filter(task_id=task_info):
                    if not Project_task_argument.objects.filter(project_task_id=prj_task, argument=a).exists():
                        Project_task_argument.objects.create(default_value=a.default_value, argument=a,
                                                             task_id=task_info,
                                                             station_id=prj_task.station_id, project_task_id=prj_task)


        new_db_args = [a.argument for a in Arguments.objects.filter(task_id=task_info)]
        for i, arg in enumerate(arguments):
            # if argument had in database will update
            if arg in db_args or arg != new_db_args[i]:
                arg_info = Arguments.objects.get(task_id=task_info, argument=new_db_args[i])
                arg_info.argument = arguments[i]
                arg_info.description = descripts[i]
                arg_info.default_value = values[i]
                arg_info.save()


        if len(error_messages) == 0:
            return JsonResponse(
                {'is_valid': True, "message": "Update  Test Case ID: [ %s ] was successfully!" % task_id,
                 "task_id": task_id}, status=200)

        return JsonResponse({'is_valid': False, "error": list(set(error_messages))}, status=500)


@login_required(login_url="/user/login/")
def modify_index(request, task_id, message=None):
    is_script = True

    u = UpdateFileForm()

    # handle the "GET" function
    a = ArgumentForm()
    task_info = Upload_TestCase.objects.get(task_id=task_id)
    args = Arguments.objects.filter(task_id=task_info)
    render_value = True
    if message !=None:
        susessful = message

    # update the attachment name
    if task_info.existed_attachment:
        attach_name = get_attach_name(task_id)

    # update testScript zip modified time
    modify_time = get_modify_time(task_id)

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
