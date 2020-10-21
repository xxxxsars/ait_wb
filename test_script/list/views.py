from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from test_script.upload.models import *

import json,os,re
from datetime import datetime

from common.handler import handle_path,get_script_list

@login_required(login_url="/user/login/")
def list_task_view(request):
    is_script = True
    task_instances = Upload_TestCase.objects.all()
    datas = get_script_list()
    return render(request, "script_list.html", locals())


