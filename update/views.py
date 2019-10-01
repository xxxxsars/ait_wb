from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response


import zipfile, os, shutil, platform, re

from update.forms import *
from update.serializer import *

from upload.models import *
from upload.forms import *


# Create your views here.

# when redirect will show message to update page
def update_index(request, message=None):
    if request.method == 'POST':
        form = QueryTestCaseForm(request.POST)

        task_id = request.POST["task_id"]
        task_name = request.POST["task_name"]

        if form.is_valid():
            # primary query condition is script_name
            u = UploadFileForm()

            task_info = ""

            if task_name != "":
                task_info = Upload_TestCase.objects.get(task_name=task_name)

            elif task_id != "":
                task_info = Upload_TestCase.objects.get(task_id=task_id)
            task_info = Upload_TestCase.objects.get(task_id=task_id)
            args = Arguments.objects.filter(task_id=task_info)

            return render(request, "modify.html", locals())

    # handle redirect GET request
    form = QueryTestCaseForm()
    if message != None and error_message(message):
        is_error = True

    return render(request, "update.html", locals())





class DeleteTestCaseView(viewsets.ModelViewSet):
    queryset = Upload_TestCase.objects.all()
    serializer_class = TaskSerializer
    http_method_names = ['delete']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            task_name = serializer.data["task_name"]
            remove_upload_file(task_name)
            self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def modify_testCase(request, format=None):
    if request.method == "POST":
        task_name = request.POST["task_name"]
        task_info = Upload_TestCase.objects.get(task_name=task_name)
        arg_infos = Arguments.objects.filter(task_id=task_info)

        # check zip file
        if "file" in request.FILES:
            try:
                handle_update_file(request.FILES['file'], task_name)
            except Exception:
                message = "Upload file is no valid zip file."
                return redirect("redirect_update", message)

        t_serialzer = TaskSerializer(task_info, data=request.data)
        # check all post agrument information is valid
        vaild = False

        # check task_case information
        if t_serialzer.is_valid():
            for arg in arg_infos:

                # value get from post
                post_arg = request.POST["arg_%s" % arg.argument]
                post_descript = request.POST["des_%s" % arg.argument]

                if vail_argument(post_arg) == False:
                    message = "Your arguments [%s] cannot contain spaces." % post_arg
                    return redirect("redirect_update", message)

                a_serialzer = ArgumentuSerializer(arg, data={"argument": post_arg,
                                                             "description": post_descript,
                                                             "task_id": request.POST["task_id"]})
                # any argument is not valid will break for loop
                if a_serialzer.is_valid():
                    a_serialzer.save()
                    t_serialzer.save()
                    vaild = True

                else:
                    vaild = False
                    break

        if vaild:
            message = "Modify TestCase successfully!"
            return redirect("redirect_update", message)

        # if data not valid return error and redirect to update page
        message = "Your modify data had some error."
        return redirect("redirect_update", message)


def vail_argument(argument):
    if re.search(r"\s", argument) != None:
        return False
    return True


def error_message(message):
    if re.match(r".+(no valid.+|.+error|.+cannot.+).+", message):
        return True
    return False




def remove_upload_file(task_name):
    path = os.path.dirname(  os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        source_folder = path + r'\upload_folder\\' + task_name

    else:
        source_folder = path+'/upload_folder/' + task_name


    # remove  script file
    try:

        print(source_folder)
        shutil.rmtree(source_folder )
    except Exception:
        pass



# handle_update_file will remove all unzip folder
def handle_update_file(f, task_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        source_zip = path + r'\upload_folder\\' + f.name
        unzip_path = path + r'\upload_folder\\'

    else:
        source_zip = path + 'upload_folder/' + f.name
        unzip_path = path + 'upload_folder/'

    with open(source_zip, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # check vaild zip file
    try:
        zip_file = zipfile.ZipFile(source_zip)
        ret = zip_file.testzip()

        if ret is not None:
            raise Exception("not valid zip")

    except Exception:
        os.remove(source_zip)
        raise Exception("Upload file is no valid zip file.")

    # remove old script file
    try:
        shutil.rmtree(unzip_path + task_name)
    except Exception:
        pass

    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(unzip_path + task_name)

    os.remove(source_zip)
