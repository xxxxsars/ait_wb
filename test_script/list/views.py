from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from test_script.upload.models import *

import json
import os

from common.handler import handle_path

@login_required(login_url="/user/login/")
def list_task(request):
    is_script = True
    datas = Upload_TestCase.objects.all()
    no_att_tasks = no_attach_tasks()

    return render(request, "script_list.html", locals())


def no_attach_tasks():
    task_infos = Upload_TestCase.objects.filter(existed_attachment = False)
    no_attach_ids = [task.task_id   for task in task_infos]
    return no_attach_ids