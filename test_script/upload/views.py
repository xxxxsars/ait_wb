from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, RemoteUserAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from test_script.upload.forms import *
from test_script.upload.models import *
import os, re
import zipfile
import platform

from common.handler import *

# Create your views here.

from django.http import HttpResponse
from common.limit import input_project_name,input_part_station

def test(request):
    p = PhotoForm()
    print(request.POST)
    if request.method == 'POST':
        p = PhotoForm(request.POST, request.FILES)

        if p.is_valid():
            if "file" in request.FILES:
                f = request.FILES.get('file0')
                if f is not None:
                    with open(os.path.join('/Users/mac/Python/Python_Project/Python/FactoryWeb/test_script/upload', f.name), 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)

                    return JsonResponse({'is_valid': True,'name': f.name,})
                else:
                    return JsonResponse({'is_valid': False})

    return render(request,'test.html',locals())

@login_required(login_url="/user/login/")
def upload_index(request):
    is_script = True
    a = ArgumentForm()
    u = UploadFileForm()
    return render(request, "upload.html", locals())



@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def upload_API(request):
    error_messages = []
    user_name = request.user.username
    if request.POST:
        print(request.POST,request.FILES)
        id = request.POST["task_id"]
        task_name = request.POST["task_name"]
        task_descript = request.POST["description"]
        script_name = request.POST["script_name"]
        sample = request.POST["sample"]
        zip_file =request.FILES['file']

        arg_descripts = request.POST.getlist("arg_description")
        arguments = request.POST.getlist("argument")
        values = request.POST.getlist("default_value")


        err = valid_zip_file(zip_file)
        if len(err)>0:
            error_messages+=err

        serial_number = "00"
        try:
            serial_number = get_serial_number(id)
        except ValueError:
            error = "Upload TestCase ID was gather then 99!"
            error_messages.append(error)


        if len(error_messages) == 0:
            task_id = id + serial_number

            up = Upload_TestCase.objects.create(task_id=task_id, task_name=task_name, description=task_descript,
                                                script_name=script_name, sample=sample,modify_user=user_name,create_user=user_name)

            for i, e in enumerate(arguments):
                argument = arguments[i]
                description = arg_descripts[i]
                value = values[i]
                Arguments.objects.create(argument=argument, description=description, default_value=value, task_id=up)


            handle_uploaded_file(zip_file, task_id)

            if 'attachment' in request.FILES:
                handle_attachment(request.FILES['attachment'], task_id)
                up.existed_attachment = True
            else:
                up.existed_attachment = False

            up.save()
            return JsonResponse({'is_valid': True,"message":"Upload  Test Case ID: [ %s ] was successfully!" % task_id,"task_id":task_id},status=200)


        return JsonResponse({'is_valid': False, "error": list(set(error_messages))}, status=500)

    return JsonResponse({'is_valid': False,"error":list(set(error_messages))},status=500)



def handle_attachment(f, task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    save_path = handle_path(path, "upload_files", task_id, "attachment")

    with open(os.path.join(save_path, f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def handle_uploaded_file(f, task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_zip = os.path.join(handle_path(path, "upload_files"), f.name)
    unzip_path = os.path.join(handle_path(path, "upload_files"), task_id)

    with open(source_zip, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(unzip_path)

    # remove zip file
    os.remove(source_zip)


def valid_zip_file(file):
    error_messages = []
    try:
        zip_file = zipfile.ZipFile(file)
        ret = zip_file.testzip()
        if ret is not None:
            error_messages.append("Upload file is no valid zip file.")
        zip_file.close()

    except Exception:
        error_messages.append("Upload file is no valid zip file.")

    return error_messages