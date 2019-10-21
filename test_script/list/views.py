from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from test_script.upload.models import *

import json



@login_required(login_url="/user/login/")
def list_task(request):
    is_script = True
    datas = Upload_TestCase.objects.all()

    return render(request, "script_list.html", locals())



def confirm(request):
    if request.POST:
        print(request.POST)
    task_ids = list(Upload_TestCase.objects.values_list("task_id",flat=True))
    arg_dict = {}
    for task_id in task_ids:
        task_info = Upload_TestCase.objects.get(task_id=task_id)
        args = Arguments.objects.filter(task_id=task_info)
        arg_dict[task_id] = list(args.values())

    arg_json = json.dumps(arg_dict)
    return render(request, "test.html", locals())


