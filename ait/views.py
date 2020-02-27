from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, RemoteUserAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import datetime
import multiprocessing
import shutil
import logging

import platform,os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django
django.setup()

from ait.forms import *
from ait.models import *

from FactoryWeb.settings import *
from common.handler import path_combine, samba_mount


# Create your views here.
@login_required(login_url="/user/login/")
def download_index(request):
    is_ait = True
    datas = AIT_release.objects.all()

    return render(request, "ait_download.html", locals())


@login_required(login_url="/user/login/")
def release_note(request, version):
    is_ait = True
    content = AIT_release.objects.get(version=version)
    return render(request, "annoucement.html", locals())


@login_required(login_url="/user/login/")
@staff_member_required
@authentication_classes((SessionAuthentication,))
def update(request, version):
    is_ait = True
    ait = AIT_release.objects.get(version=version)
    is_update = True
    u = UploadAITForm()
    return render(request, "ait_upload.html", locals())


@login_required(login_url="/user/login/")
@staff_member_required
@authentication_classes((SessionAuthentication,))
def update_message(request, version, message):
    is_ait = True
    ait = AIT_release.objects.get(version=version)
    is_update = True
    u = UploadAITForm()

    return render(request, "ait_upload.html", locals())


@login_required(login_url="/user/login/")
@staff_member_required
@authentication_classes((SessionAuthentication,))
def upload(request):
    is_ait = True
    u = UploadAITForm()
    return render(request, "ait_upload.html", locals())


@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def download(request):
    path = os.path.dirname(os.path.abspath(__file__))
    file_path = path_combine(path,'ait_jar',"AIT.jar")

    file = open(file_path, 'rb')
    response = StreamingHttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="AIT.jar"'
    return response

# update AIT file
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
            # mount samba folder
            try:
                samba_mount()
            except Exception as e:

                return JsonResponse({"valid": False, "message": "Connection failed."},
                                    status=status.HTTP_408_REQUEST_TIMEOUT)

            handle_uploaded_file(request.FILES['file'])

        ait.save()

        return JsonResponse({'is_valid': True, "message": "Update AIT was successfully!!"}, status=200)

    return JsonResponse({'is_valid': False, "message": "Update AIT was failed."}, status=400)


# upload AIT file
@api_view(["POST"])
@authentication_classes((SessionAuthentication,))
def upload_API(request):
    if request.POST:

        u = UploadAITForm(request.POST, request.FILES)

        if u.is_valid():

            version = request.POST['version']
            release_note = request.POST['release_note']
            if version != "" and release_note != "" and 'file' in request.FILES:
                AIT_release.objects.create(version=version, release_note=release_note)

                # mount samba folder
                try:
                    samba_mount()
                except Exception as e:

                    return JsonResponse({"valid": False, "message": "Connection failed."},
                                        status=status.HTTP_408_REQUEST_TIMEOUT)


                handle_uploaded_file(request.FILES['file'])
                return JsonResponse({'is_valid': True, "message": "Update AIT was successfully!!"}, status=200)
            else:
                return JsonResponse({'is_valid': False, "message": "Your must be provided file and version."},
                                    status=400)

    return JsonResponse({'is_valid': False, "message": "Update AIT was failed."}, status=400)


@api_view(["GET"])
@authentication_classes((SessionAuthentication,))
def valid_ait_version(request):
    if request.GET:
        version = request.GET["version"]
        if AIT_release.objects.filter(version=version).count():
            return JsonResponse({"valid": False})
        else:
            return JsonResponse({"valid": True})


@api_view(["POST"])
@authentication_classes((SessionAuthentication, BasicAuthentication))
def delete_release_version(request):
    if request.method == "POST":
        version = request.data.get("version")
        if version == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance = AIT_release.objects.filter(version=version)

        if instance.exists() == False:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance.first().delete()

        # if ait_release table had emptied ,it will remove AIT.jar
        if len(AIT_release.objects.all()) == 0:
            path = path_combine(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ait_jar", "AIT.jar")
            os.remove(path)

        return Response(status=status.HTTP_200_OK)


def copy_to_samba(source,target):
    try:
        shutil.copy(source, target)
    except Exception as e:


        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"log")
        if os.path.exists(path) == False:
            os.mkdir(path)
        log_filename = datetime.datetime.now().strftime( os.path.join(path,"AIT-%Y-%m-%d.log"))
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=log_filename)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

        console.setFormatter(formatter)

        logging.getLogger('').addHandler(console)
        logging.info(e)


def handle_uploaded_file(f):
    path = os.path.dirname(os.path.abspath(__file__))

    if platform.system() == "Windows":
        samba_path =  path_combine(WIN_MOUNT_PATH,"AIT.jar")
    else:
        samba_path = path_combine(OSX_MOUNT_PATH,"AIT.jar")

    save_path = path_combine(path, 'ait_jar', "AIT.jar")

    with open(os.path.join(save_path), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # copy AIT.jar to samba in background
    p = multiprocessing.Process(target=copy_to_samba, args=(save_path, samba_path,))
    p.start()














