from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import zipfile,os,shutil

from update.forms import *
from update.serializer import *

from upload.models import *


# Create your views here.


def update_index(request):
    if request.method == 'POST':
        form = QueryTestCaseForm(request.POST)



        task_id = request.POST["task_id"]
        script_name = request.POST["script_name"]


        if task_id == "" and script_name == "":
            error = "Your must be provide ID or Script Name to inquire data."


        if form.is_valid():
            # primary query condition is script_name
            if script_name != "":
                datas = Upload_TestCase.objects.filter(script_name=script_name)

            elif task_id != "":
                datas = Upload_TestCase.objects.filter(task_id=task_id)

            return render(request, "modify.html", locals())
    else:
        form = QueryTestCaseForm()

    return render(request, "update.html", locals())


@api_view(["POST"])
def modify_testCase(request, format=None):
    if request.method == "POST":
        script_name = request.POST["script_name"]
        obj = Upload_TestCase.objects.get(script_name=script_name)
        serialzer = ModifySerializer(obj, data=request.data)


        # check zip file
        handle_update_file(request.FILES['file'], script_name)


        # check others parameters
        if serialzer.is_valid():
            serialzer.save()


            return redirect("script_update")

        return Response(serialzer.errors, status=status.HTTP_400_BAD_REQUEST)


# handle_update_file will remove all unzip folder
def handle_update_file(f,script_name):
    source_zip = 'upload_folder/'+f.name

    with open(source_zip, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


    # remove old script file
    try:
        shutil.rmtree('upload_folder/'+script_name)
    except Exception:
        pass


    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall('upload_folder/'+script_name)

    os.remove(source_zip)