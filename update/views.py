from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import zipfile,os,shutil,platform,re

from update.forms import *
from update.serializer import *

from upload.models import *


# Create your views here.

# when redirect will show message to update page
def update_index(request,message=None):

    if request.method == 'POST':
        form = QueryTestCaseForm(request.POST)



        task_id = request.POST["task_id"]
        script_name = request.POST["script_name"]


        if task_id == "" and script_name == "":
            error = "Your must be provide ID or Script Name to inquire data."


        if form.is_valid():
            # primary query condition is script_name
            if script_name != "":
                task_info = Upload_TestCase.objects.get(script_name=script_name)
                args = Arguments.objects.filter(task_id=task_info)

            elif task_id != "":
                task_info = Upload_TestCase.objects.get(task_id=task_id)
                args = Arguments.objects.filter(task_id=task_info)


            return render(request, "modify.html", locals())

    else:
        form = QueryTestCaseForm()


    if message!=None:
        if re.match(r".+(no valid.+|.+error).+", message):
            is_error =True



    return render(request, "update.html", locals())


@api_view(["POST"])
def modify_testCase(request, format=None):
    if request.method == "POST":
        script_name = request.POST["script_name"]
        obj = Upload_TestCase.objects.get(script_name=script_name)
        serialzer = ModifySerializer(obj, data=request.data)

        # check zip file
        if  "file" in request.FILES:
            try:
                handle_update_file(request.FILES['file'], script_name)
            except Exception:
                message = "Upload file is no valid zip file."
                return redirect("redirect_update",message)


        # check others parameters
        if serialzer.is_valid():
            serialzer.save()
            message = "Modify TestCase successfully!"
            return redirect("redirect_update",message)



        # if data not valid return error and redirect to update page
        message = "Your modify data had some error."
        return redirect("redirect_update", message)


# handle_update_file will remove all unzip folder
def handle_update_file(f,script_name):
    path = os.path.dirname(os.path.abspath(__file__))

    if platform.system() =="Windows":
        source_zip = path + r'\upload_folder\\' + f.name
        unzip_path = path +r'\upload_folder\\'

    else:
        source_zip = 'upload_folder/'+f.name
        unzip_path = 'upload_folder/'

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
        shutil.rmtree(unzip_path+script_name)
    except Exception:
        pass


    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(unzip_path+script_name)

    os.remove(source_zip)