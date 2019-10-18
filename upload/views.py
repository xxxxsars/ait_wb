from django.shortcuts import render
from django.http import JsonResponse
from upload.forms import *
from upload.models import *
import os
import zipfile
import platform
import shutil

# Create your views here.

def upload_index(request):
    is_script = True

    if request.method == 'POST':
        a = ArgumentForm(request.POST)
        u = UploadFileForm(request.POST, request.FILES)



        if u.is_valid() and a.is_valid():
            id = request.POST["task_id"]
            task_name = request.POST["task_name"]
            task_descript = request.POST["task_description"]
            script_name = request.POST["script_name"]



            descripts = request.POST.getlist("description")
            arguments =request.POST.getlist("argument")
            values = request.POST.getlist("default_value")



            try:
                serial_number = get_serial_number(id)
            except ValueError:
                error_message = "Upload TestCase ID was gather then 99!"
                return render(request, "upload.html", locals())



            task_id = id +serial_number


            handle_uploaded_file(request.FILES['file'],task_name)


            up = Upload_TestCase.objects.create(task_id=task_id,   task_name=task_name,description = task_descript,  script_name=script_name)

            for i, e in enumerate(arguments):
                argument = arguments[i]
                description = descripts[i]
                value = values[i]
                Arguments.objects.create(argument=argument, description=description,default_value= value ,task_id=up)


            susessful = "Upload  Test Case ID: [ %s ] was successfully!" % task_id
            return render(request, "upload.html", locals())
    else:
        a = ArgumentForm()
        u = UploadFileForm()




    return render(request,"upload.html",locals())

def get_serial_number(task_id):
    datas = Upload_TestCase.objects.filter(task_id__iregex=r"^%s\d{2}"%task_id).values()
    if len(datas) == 0:
        return "00"
    serials = []
    for data in datas:
        serial = re.search(r'(\d{2})$', data["task_id"]).group(1)
        serials.append(int(serial))


    serial_number = max(serials)+1

    if serial_number >99:
        raise ValueError("Your serial id is gather than 99.")

    max_serial = "%02d" % serial_number

    return max_serial

def handle_uploaded_file(f,task_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        source_zip = path + r'\upload_folder\\' + f.name
        unzip_path = path + r'\upload_folder\\'

    else:
        source_zip = path + '/upload_folder/' + f.name
        unzip_path = path + '/upload_folder/'


    with open(source_zip, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)



    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(unzip_path+task_name)

    # remove zip file
    os.remove(source_zip)

