from django.shortcuts import render
from django.http import StreamingHttpResponse,Http404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

import os
import platform
from ait.forms import *
from ait.models import *
# Create your views here.


@login_required(login_url="/user/login/")
def download_index(request):
    is_ait = True
    datas = AIT_release.objects.all()



    return render(request,"ait_download.html",locals())




@login_required(login_url="/user/login/")
def download(request):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if platform.system() == "Windows":
        file_path = path + r'\ait_jar\\' + "AIT.jar"

    else:
        file_path = path + '/ait_jar/' + "AIT.jar"


    file = open(file_path, 'rb')
    response = StreamingHttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="AIT.jar"'
    return response


@login_required(login_url="/user/login/")
def release_note(request,version):

    content = AIT_release.objects.get(version=version)



    return render(request,"annoucement.html",locals())


@login_required(login_url="/user/login/")
@staff_member_required
def upload(request):
    is_ait = True
    if request.POST:

        u = UploadAITForm(request.POST, request.FILES)


        if u.is_valid():

            version = request.POST['version']
            release_note = request.POST['release_note']
            if version !="" and release_note !="":

                AIT_release.objects.create(version=version,release_note=release_note)

            handle_uploaded_file(request.FILES['file'])
            susessful = "Upload AIT was successfully!!"
            # clean all data
            u = UploadAITForm()
        else:
            u = UploadAITForm(request.POST,request.FILES)

        return render(request, "ait_upload.html", locals())

    else:

        u = UploadAITForm()

    return render(request, "ait_upload.html", locals())




def handle_uploaded_file(f):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        save_path = path + r'\ait_jar\\' + "AIT.jar"

    else:
        save_path = path + '/ait_jar/' + "AIT.jar"


    with open(save_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

