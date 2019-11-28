from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
    if request.method == 'POST':
        p = PhotoForm(request.POST, request.FILES)
        if p.is_valid():
            if "file" in request.FILES:
                f = request.FILES.get('file')
                if f is not None:
                    with open(os.path.join('/Users/mac/Python/Python_Project/Python/FactoryWeb/test_script/upload', f.name), 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)

                    return JsonResponse({'is_valid': True,'name': f.name,})
                else:
                    return JsonResponse({'is_valid': False})

    return render(request,'test.html',locals())

def upload_API(request):
    error_messages = []

    if request.POST:
        print(request.POST,request.FILES)

        id = request.POST["task_id"]
        task_name = request.POST["task_name"]
        task_descript = request.POST["task_description"]
        script_name = request.POST["script_name"]
        sample = request.POST["sample"]
        zip_file =request.FILES['file']

        descripts = request.POST.getlist("description")
        arguments = request.POST.getlist("argument")
        values = request.POST.getlist("default_value")


        err = valid_task_info(id,task_name,script_name,zip_file)
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
                                                script_name=script_name, sample=sample)

            post_args = []
            arg_to_db = []
            for i, e in enumerate(arguments):
                argument = arguments[i]
                description = descripts[i]
                value = values[i]

                # check the argument
                if argument in post_args:
                    error = "Your arguments only allow unique values."
                    error_messages.append(error)
                else:
                    if input_argument.search(argument) != None:
                        error= "Your arguments only allow number, letter and underline."
                        error_messages.append(error)
                    else:
                        post_args.append(argument)

                # check default value
                if valid_default_value(value) == False:
                    error = "Your default value does not match the rule."
                    error_messages.append(error)


                if len(error_messages) ==0:
                   arg_to_db.append( Arguments(argument=argument, description=description, default_value=value, task_id=up))


            # Both argument and testCase information are corrent will save all paramter and upload file.
            if len(error_messages) == 0:
                for a in arg_to_db:
                    a.save()

                handle_uploaded_file(zip_file, task_id)

                if 'attachment' in request.FILES:
                    handle_attachment(request.FILES['attachment'], task_id)
                    up.existed_attachment = True
                else:
                    up.existed_attachment = False

                return JsonResponse({'is_valid': True,"message":"Upload  Test Case ID: [ %s ] was successfully!" % task_id,"task_id":task_id},status=200)

            # if argument had error will delete task information from database.
            else:
                up.delete()

            return JsonResponse({'is_valid': False, "error": list(set(error_messages))}, status=500)

    return JsonResponse({'is_valid': False,"error":list(set(error_messages))},status=500)



def valid_task_info(id,task_name,script_name,file):
    error_messages = []
    if input_task_id.search(id) == None:
        error_messages.append("Your ID not match the ID rules.")

    if Upload_TestCase.objects.filter(task_name=task_name).count():
        error_messages.append("Your TestCase Name cannot be repeated.Please Update it.")


    if input_task_name.search(task_name) != None:
        error_messages.append("Your TestCase Name only allow number, letter and underline.")

    if  input_script_name.search(script_name) == None:
        error_messages.append(
            'Your Script Name needs to contain a filename extension and the name only allow number, letter and underline.')

    if input_zip_file_name.search(str(file)) == None:
        error_messages.append("Upload file is no valid zip file.")

    try:
        zip_file = zipfile.ZipFile(file)
        ret = zip_file.testzip()
        if ret is not None:
            error_messages.append("Upload file is no valid zip file.")
        zip_file.close()

    except Exception:
        error_messages.append("Upload file is no valid zip file.")

    return error_messages



@login_required(login_url="/user/login/")
def upload_index(request):
    is_script = True
    a = ArgumentForm()
    u = UploadFileForm()



    # print(request.POST,request.FILES)
    # if request.method == 'POST':
    #     datas = dict(request.POST)
    #     a = ArgumentForm(request.POST)
    #     u = UploadFileForm(request.POST, request.FILES)
    #
    #     if u.is_valid() and a.is_valid():
    #         id = request.POST["task_id"]
    #         task_name = request.POST["task_name"]
    #         task_descript = request.POST["task_description"]
    #         script_name = request.POST["script_name"]
    #         sample = request.POST["sample"]
    #
    #         descripts = request.POST.getlist("description")
    #         arguments = request.POST.getlist("argument")
    #         values = request.POST.getlist("default_value")
    #
    #         try:
    #             serial_number = get_serial_number(id)
    #         except ValueError:
    #             error_message = "Upload TestCase ID was gather then 99!"
    #             return render(request, "upload.html", locals())
    #
    #         task_id = id + serial_number
    #
    #         handle_uploaded_file(request.FILES['file'], task_id)
    #
    #         up = Upload_TestCase.objects.create(task_id=task_id, task_name=task_name, description=task_descript,
    #                                             script_name=script_name, sample=sample)
    #
    #         if 'attachment' in request.FILES:
    #             handle_attachment(request.FILES['attachment'], task_id)
    #             up.existed_attachment = True
    #         else:
    #             up.existed_attachment = False
    #
    #         post_args = []
    #         for i, e in enumerate(arguments):
    #             argument = arguments[i]
    #             description = descripts[i]
    #             value = values[i]
    #
    #             # check the argument
    #             if argument in post_args:
    #                 error_message = "Your arguments only allow unique values."
    #                 return render(request, "upload.html", locals())
    #             else:
    #                 if input_argument.search(argument) != None:
    #                     error_message = "Your arguments only allow number, letter and underline."
    #                     return render(request, "upload.html", locals())
    #                 else:
    #                     post_args.append(argument)
    #
    #             # check default value
    #             if valid_default_value(value) == False:
    #                 error_message = "Your default value does not match the rule."
    #                 return render(request, "upload.html", locals())
    #
    #             Arguments.objects.create(argument=argument, description=description, default_value=value, task_id=up)
    #
    #         susessful = "Upload  Test Case ID: [ %s ] was successfully!" % task_id
    #         return redirect("/testCase/modify/%s/%s" % (task_id, susessful))

    return render(request, "upload.html", locals())


def handle_attachment(f, task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    save_path = handle_path(path, "upload_folder", task_id, "attachment")

    with open(os.path.join(save_path, f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def handle_uploaded_file(f, task_id):
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_zip = os.path.join(handle_path(path, "upload_folder"), f.name)
    unzip_path = os.path.join(handle_path(path, "upload_folder"), task_id)

    with open(source_zip, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(unzip_path)

    # remove zip file
    os.remove(source_zip)
