from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, RemoteUserAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

import os
import shutil
import platform
import collections
import re

from common.handler import *

from test_script.update.forms import *
from test_script.upload.forms import *
from common.limit import input_argument, valid_default_value
from common.handler import handle_path, get_attach_name, get_modify_time
from project.models import *

@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def update_API_view(request):
    error_messages = []
    if request.POST:

        task_id = request.POST.get("task_id")
        task_name = request.POST.get("task_name")
        task_descript = request.POST.get("description")
        script_name = request.POST.get("script_name")
        sample = request.POST.get("sample")
        interactive = request.POST.get("interactive")
        task_info = Upload_TestCase.objects.get(task_id=task_id)


        # check error
        if "file" in request.FILES:
            errors = handle_update_file(request.FILES['file'], task_id)

            if len(errors)>0:
                error_messages+= errors
        else:
            if task_info.script_name != script_name:
                error_messages.append("Modify the script name must be re-uploaded TestScript.zip.")


        # if had error will return error and not save modify data
        if len(error_messages) > 0:
            return JsonResponse({'is_valid': False, "error": list(set(error_messages))}, status=500)


        if 'attachment' in request.FILES:
            handle_update_attachment(request.FILES['attachment'], task_id)
            task_info.existed_attachment = True
            # attach_name = request.FILES["attachment"].name

        # if interactive item only save those item.
        if interactive =="True":
            task_info.task_name = task_name
            task_info.time = datetime.datetime.now()
            task_info.description = task_descript
            task_info.save()

            if len(error_messages) == 0:
                return JsonResponse(
                    {'is_valid': True, "message": "Update  Test Case ID: [ %s ] was successfully!" % task_id,
                     "task_id": task_id}, status=200)

            return JsonResponse({'is_valid': False, "error": list(set(error_messages))}, status=500)

        # not interactive item will do...
        else:
            is_modify = had_modify(request)

            if (is_modify and len(error_messages)<=0 and "file" in request.FILES):
                task_info.modify_user = request.user.username
                try:
                    new_version = update_version(task_info.version)
                except ValueError as e:
                    err = [str(e)]
                    return JsonResponse({'is_valid': False, "error": err}, status=417)
                task_info.version = new_version
                task_info.time = datetime.datetime.now()

            # handle post task information
            task_info.task_name = task_name
            task_info.script_name = script_name
            task_info.description = task_descript
            task_info.sample = sample

            task_info.save()

            db_args = [a.argument for a in Arguments.objects.filter(task_id=task_info)]

            arg_descripts = request.POST.getlist("arg_description")
            arguments = request.POST.getlist("argument")
            values = request.POST.getlist("default_value")


            # if post argument more than database argument will create it.
            if len(arguments) > len(db_args):
                index = len(db_args)
                new_args =arguments[index::]

                for i,arg in  enumerate(new_args):
                    argument = arguments[index+i]
                    description = arg_descripts[index+i]
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
                    arg_info.description = arg_descripts[i]
                    arg_info.default_value = values[i]
                    arg_info.save()


            if len(error_messages) == 0:
                return JsonResponse(
                    {'is_valid': True, "message": "Update  Test Case ID: [ %s ] was successfully!" % task_id,
                     "task_id": task_id}, status=200)

            return JsonResponse({'is_valid': False, "error": list(set(error_messages))}, status=500)

@login_required(login_url="/user/login/")
def modify_index_view(request, task_id, message=None):
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
    if task_info.script_name =="interactive":
        modify_time = ""
    else:
        modify_time = get_modify_time(task_id)

    return render(request, "script_modify.html", locals())

def update_version(version:str) ->str:
    regex = re.compile(r"^(\d){1}\.(\d{2})$")

    matched = regex.search(version)
    if matched:
        first_number = int(matched.group(1))
        second_number = int(matched.group(2))

        if second_number+1 >=99:
            first_number +=1
            second_number = 1

            if first_number >9:
                raise ValueError("Limit number of edits has been exceeded")

        else:
            second_number +=1

        return "%d.%02d"%(first_number,second_number)
    else:
        raise ValueError("Version content is not match")

def had_modify(request) ->bool:
    # check testCase.zip had been modified
    if "file" in request.FILES:
        return True

    # check testCase object had been modified
    testCase_instance = Upload_TestCase.objects.get(task_id = request.POST["task_id"])
    origin=  model_to_dict(testCase_instance)

    for key,value in dict(request.POST).items():
        if key in origin:
            if value[0] !=origin[key]:
                return True
    # check post data is more than db data.
    db_args = [a.argument for a in Arguments.objects.filter(task_id=testCase_instance)]
    arguments = request.POST.getlist("argument")
    if len(arguments) > len(db_args):
        return True

    #check arguments had been modified
    arg_descripts = request.POST.getlist("arg_description")
    values = request.POST.getlist("default_value")

    db_args = Arguments.objects.filter(task_id=testCase_instance)
    for i, arg in enumerate(arguments):
        if arguments[i] != db_args[i].argument:
            return True
        if arg_descripts[i] != db_args[i].description:
            return True
        if values[i] != db_args[i].default_value:
            return True
    return False

def handle_update_attachment(f, task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    save_path = handle_path(path, "upload_files", task_id, "attachment")

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
    error_messages = []
    if input_zip_file_name.search(str(f.name)) == None:
        raise Exception("Upload file is no valid zip file.")

    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_zip = os.path.join(handle_path(path, "upload_files"), f.name)
    unzip_path = os.path.join(handle_path(path, "upload_files"), task_id)

    with open(source_zip, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # check vaild zip file
    errors = valid_zip_file(source_zip,task_id)
    if len(errors) >0:
        error_messages+=errors
        return error_messages

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

    return  error_messages