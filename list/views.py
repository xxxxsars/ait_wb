


from django.shortcuts import render, redirect
from django_tables2 import RequestConfig
from upload.models import *
import re


# Create your views here.


def list_index(request):
    datas = Upload_TestCase.objects.all()

    if request.POST:

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
        else:
            reg =re.compile(r'arg_([0-9A]+)_(\w+)')

            result_dict = {}
            for k,v in  dict(request.POST.lists()).items():
                pd = []
                if reg.match(k):
                    task_id = reg.search(k).group(1)
                    script_name = Upload_TestCase.objects.get(task_id=task_id).script_name
                    parmeter = reg.search(k).group(2)
                    argument = v[0]

                    if task_id in result_dict:
                        pd = result_dict[task_id]
                        pd[parmeter] = argument
                    else:
                        result_dict[task_id] = {parmeter:argument,"script_name":script_name}






            print(result_dict)



    return render(request, "list.html", locals())


def set_argument(request):
    if request.POST:
        print(request.POST)

    return render(request, "set_argument.html", locals())



def get_parameter_order(task_id,argument):
    task_info = Upload_TestCase.objects.filter(task_id=task_id)
    arg = Arguments.objects.filter(task_id=task_info).get(argument=argument)
    return arg.id


def gen_ini_str(task_id):
    d  = {'000003': {'tret': '1', 'script_name': 'dsf', 'wrtert': '2', 'sdfsdfds': '3'}, '000004': {'123': '4', 'script_name': 'fgdfg'}}

    print(d[task_id])


    result = "[0_AUTO_%s_%s]"

