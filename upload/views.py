from django.shortcuts import render
from upload.forms import *
from upload.models import *
import os
import zipfile
import platform

# Create your views here.

def upload_index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)


        if form.is_valid():


            task_id = request.POST["task_id"]
            script_name = request.POST["script_name"]
            descript = request.POST["description"]
            exec_time = request.POST["exec_time"]
            argument = request.POST["argument"]


            handle_uploaded_file(request.FILES['file'],script_name)

            up = Upload_TestCase(task_id=task_id,script_name=script_name,description=descript,exec_time=exec_time,argument=argument)
            up.save()


            susessful = "Upload  Test Case ID: [ %s ] was successfully!" % task_id
            return render(request, "upload.html", locals())
    else:
        form = UploadFileForm()



    return render(request,"upload.html",locals())




def handle_uploaded_file(f,script_name):
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



    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(unzip_path+script_name)

    # remove zip file
    os.remove(source_zip)
