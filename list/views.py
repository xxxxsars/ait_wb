from django.shortcuts import render, redirect
from django_tables2 import RequestConfig
from upload.models import *


# Create your views here.


def list_index(request):
    datas = Upload_TestCase.objects.all()

    if request.POST:
        task_ids = (request.POST['task_ids']).split(",")



        arg_dict = {}
        if len(task_ids) != 0:
            for task_id in task_ids:
                task_info = Upload_TestCase.objects.get(task_id=task_id)
                args = Arguments.objects.filter(task_id=task_info)

                arg_dict[task_id] = args.values()


            print(arg_dict)


            return render(request, "set_argument.html", locals())


    return render(request, "list.html", locals())


def set_argument(request):
    if request.POST:
        print(request.POST)

    return render(request, "set_argument.html", locals())
