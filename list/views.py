from django.shortcuts import render
from django_tables2 import RequestConfig
from upload.models import  *
# Create your views here.


def list_index(request):
    datas = Upload_TestCase.objects.all()

    if request.method == "POST":
        print(request.POST)


    return render(request,"list.html",locals())