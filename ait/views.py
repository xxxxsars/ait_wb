from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, Http404,JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, RemoteUserAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import os
import platform
from ait.forms import *
from ait.models import *


# Create your views here.
@login_required(login_url="/user/login/")
def download_index(request):
    is_ait = True
    datas = AIT_release.objects.all()

    return render(request, "ait_download.html", locals())


@login_required(login_url="/user/login/")
def release_note(request, version):
    content = AIT_release.objects.get(version=version)
    return render(request, "annoucement.html", locals())



@login_required(login_url="/user/login/")
@staff_member_required
@authentication_classes((SessionAuthentication,))
def update(request,version):
    ait = AIT_release.objects.get(version=version)
    is_update = True
    u = UploadAITForm()
    return render(request, "ait_upload.html", locals())


@login_required(login_url="/user/login/")
@staff_member_required
@authentication_classes((SessionAuthentication,))
def update_message(request,version,message):
    ait = AIT_release.objects.get(version=version)
    is_update = True
    u = UploadAITForm()

    return render(request, "ait_upload.html", locals())


@login_required(login_url="/user/login/")
@staff_member_required
@authentication_classes((SessionAuthentication,))
def upload(request):
    u = UploadAITForm()
    return render(request, "ait_upload.html", locals())




@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
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

@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def update_API(request):
    if request.method == "POST":

        version = request.POST['version']
        release_note = request.POST['release_note']

        ait = AIT_release.objects.get(version=version)
        ait.version = version
        ait.release_note = release_note

        if 'file' in request.FILES:
            handle_uploaded_file(request.FILES['file'])
        ait.save()

        return JsonResponse( {'is_valid': True, "message": "Update AIT was successfully!!"}, status=200)

    return JsonResponse( {'is_valid': False, "message": "Update AIT was failed."}, status=400)

@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def upload_API(request):

    if request.POST:
        print(request.POST)
        u = UploadAITForm(request.POST, request.FILES)

        if u.is_valid():

            version = request.POST['version']
            release_note = request.POST['release_note']
            if version != "" and release_note != "" and  'file' in request.FILES:
                AIT_release.objects.create(version=version, release_note=release_note)
                handle_uploaded_file(request.FILES['file'])
                return JsonResponse({'is_valid': True, "message": "Update AIT was successfully!!"}, status=200)
            else:
                return JsonResponse({'is_valid': False, "message": "Your must be provided file and version."}, status=400)


    return JsonResponse( {'is_valid': False, "message": "Update AIT was failed."}, status=400)

@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def valid_ait_version(request):
    if request.GET:
        version = request.GET["version"]
        if AIT_release.objects.filter(version=version).count():
            return JsonResponse({"valid":False})
        else:
            return JsonResponse({"valid": True})


def handle_uploaded_file(f):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        save_path = path + r'\ait_jar\\' + "AIT.jar"

    else:
        save_path = path + '/ait_jar/' + "AIT.jar"

    with open(save_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
