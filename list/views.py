import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django

django.setup()

from django.shortcuts import render, redirect
from django_tables2 import RequestConfig
from upload.models import *
import re


# Create your views here.


def list_index(request):
    datas = Upload_TestCase.objects.all()

    if request.POST:
        # render the set_agrument page ,it data get from list page
        if "task_ids" in request.POST:
            task_ids = (request.POST['task_ids']).split(",")
            arg_dict = {}
            if len(task_ids) != 0:
                for task_id in task_ids:
                    task_info = Upload_TestCase.objects.get(task_id=task_id)
                    args = Arguments.objects.filter(task_id=task_info)
                    arg_dict[task_id] = args.values()
                return render(request, "set_argument.html", locals())


        # todo confirm page

        # handle the set_argument submit action ,it will get all tab parameter
        else:

            task_ids = []
            arg_reg = re.compile(r'arg_([0-9A]+)_(\w+)')
            other_reg = re.compile(r"^\w+_([0-9A]{6})$")

            result_dict = {}

            print(dict(request.POST.lists()).items())
            for k, v in dict(request.POST.lists()).items():
                pd = []

                if arg_reg.match(k):
                    task_id = arg_reg.search(k).group(1)


                    if task_id not in task_ids:
                        task_ids.append(task_id)

                    task_info = Upload_TestCase.objects.get(task_id=task_id)
                    script_name = task_info.script_name
                    task_name = task_info.task_case_name

                    parmeter = arg_reg.search(k).group(2)
                    argument = v[0]

                    if task_id in result_dict:
                        pd = result_dict[task_id]
                        pd[parmeter] = argument
                    else:
                        result_dict[task_id] = {parmeter: argument,
                                                "script_name": script_name, "task_name": task_name}

            for task_id in task_ids:
                append_dict = result_dict[task_id]
                append_dict["timeout"] = request.POST["timeout_%s" % task_id]
                append_dict["exitcode"] = request.POST["exitcode_%s" % task_id]
                append_dict["retry"] = request.POST["retry_%s" % task_id]
                append_dict["sleep"] = request.POST["sleep_%s" % task_id]
                append_dict["criteria"] = request.POST["criteria_%s" % task_id]

            render_str = ""
            for task_id in task_ids:
                render_str += gen_ini_str(task_id,result_dict)+"\n"

            return render(request,"confirm.html",{"render_str":render_str})


    return render(request, "list.html", locals())


def set_argument(request):
    if request.POST:
        print(request.POST)

    return render(request, "set_argument.html", locals())


def get_parameter_order(task_id, argument):
    task_info = Upload_TestCase.objects.filter(task_id=task_id)
    arg = Arguments.objects.filter(task_id=task_info).get(argument=argument)
    return arg.id


def gen_ini_str(task_id, argumet_dict):
    di = argumet_dict[task_id]

    task_name = di["task_name"]
    script_name = di["script_name"]

    title = "[0_AUTO_%s_%s]\n" % (task_id, task_name)

    script_path = r'cmd=TestScriptRes\\%s' % script_name
    arg_str = ""
    argumes = Arguments.objects.filter(task_id=task_id)

    for arg in argumes:
        arg_str += " %s" % di[arg.argument]

    content = "%s%s;%s;%s;%s;%s\ncriteria=%s" % (
    script_path, arg_str, di["timeout"], di["exitcode"], di["retry"], di["sleep"], di["criteria"])

    return title + content



