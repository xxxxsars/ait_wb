from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from test_script.upload.forms import *
from test_script.upload.models import *
import os, re
import zipfile
import platform

from common.handler import *

# Create your views here.

@login_required(login_url="/user/login/")
def upload_index(request):
    is_script = True
    if request.method == 'POST':
        datas = dict(request.POST)
        a = ArgumentForm(request.POST)
        u = UploadFileForm(request.POST, request.FILES)

        if u.is_valid() and a.is_valid():
            id = request.POST["task_id"]
            task_name = request.POST["task_name"]
            task_descript = request.POST["task_description"]
            script_name = request.POST["script_name"]
            sample = request.POST["sample"]

            descripts = request.POST.getlist("description")
            arguments = request.POST.getlist("argument")
            values = request.POST.getlist("default_value")

            try:
                serial_number = get_serial_number(id)
            except ValueError:
                error_message = "Upload TestCase ID was gather then 99!"
                return render(request, "upload.html", locals())

            task_id = id + serial_number

            handle_uploaded_file(request.FILES['file'], task_id)



            up = Upload_TestCase.objects.create(task_id=task_id, task_name=task_name, description=task_descript,
                                                script_name=script_name,sample=sample)

            if 'attachment' in request.FILES:
                handle_attachment(request.FILES['attachment'],task_id)
                up.existed_attachment = True
            else:
                up.existed_attachment = False

            post_args = []
            for i, e in enumerate(arguments):
                argument = arguments[i]
                description = descripts[i]
                value = values[i]

                # check the argument
                if argument in post_args:
                    error_message = "Your arguments only allow unique values."
                    return render(request, "upload.html", locals())
                else:
                    if input_argument.search(argument) != None:
                        error_message = "Your arguments only allow number, letter and underline."
                        return render(request, "upload.html", locals())
                    else:
                        post_args.append(argument)

                # check default value
                if valid_default_value(value) == False:
                    error_message = "Your default value does not match the rule."
                    return render(request, "upload.html", locals())


                Arguments.objects.create(argument=argument, description=description, default_value=value, task_id=up)

            susessful = "Upload  Test Case ID: [ %s ] was successfully!" % task_id
            return redirect("/testCase/modify/%s/%s" % (task_id, susessful))

    else:
        a = ArgumentForm()
        u = UploadFileForm()

    return render(request, "upload.html", locals())


def handle_attachment(f,task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    save_path = handle_path(path,"upload_folder",task_id,"attachment")

    with open(os.path.join(save_path,f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)




def handle_uploaded_file(f, task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_zip = os.path.join(handle_path(path,"upload_folder"),f.name)
    unzip_path = os.path.join(handle_path(path,"upload_folder"),task_id)

    with open(source_zip, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(unzip_path)

    # remove zip file
    os.remove(source_zip)
