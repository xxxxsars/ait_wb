import re




# set parameter regex find input id
set_parameter_arg= re.compile(r'arg_([0-9A]+)_(.+)')
set_parameter_other = re.compile(r"^\w+_([0-9A]{6})$")



# form regex
input_task_id = re.compile(r"^[0-2][0-9A]\d{2}$")
input_task_name = re.compile(r"[^\w|_|\s]+")
input_argument = re.compile(r"[^\w|_]+")


input_project_name = re.compile(r"^\w{7}$")


def valid_default_value(value):
    if re.search("\s+",value):
        if re.search(r'^".*"$',value) ==None:
            return False

    elif re.search('[^(\w|\-|\.|")]+',value) !=None:
        return False

    return True





input_script_name = re.compile("^[\w|_]+.py$")
input_zip_file_name =  re.compile(r"\.zip$")





import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django
django.setup()
# from django.core.exceptions import ObjectDoesNotExist
# from django.db.models import Q
from test_script.upload.models import *

import platform,os,zipfile

from test_script.upload.models import *


# old id must be full id ,the new_id only input 4 number
def modify_task_id(old_id,new_id):
    old_instance = Upload_TestCase.objects.filter(task_id=old_id)

    if old_instance.exists() ==False:
        raise ValueError("Your provide Task ID had error")

    task_instance = old_instance[0]


    task_name  =task_instance.task_name

    id = new_id+get_serial_number(new_id)
    print(id)
    new_task_instance = Upload_TestCase.objects.create(task_id=id,
                                                       task_name="",
                                                       description=task_instance.description,
                                                       script_name=task_instance.script_name)

    arguments_table = Arguments.objects.filter(task_id=task_instance)


    for arg in arguments_table:
        arg.task_id= new_task_instance
        arg.save()


    task_instance.delete()
    new_task_instance.task_name= task_name
    new_task_instance.save()


#must back your upload folder and database
def modify_save_folder():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        source_path = path + r'\upload_folder\\'


    else:
        source_path = path + '/upload_folder/'


    for f in os.listdir(source_path):
        task_id = Upload_TestCase.objects.get(task_name=f).task_id
        os.rename(os.path.join(source_path, f), os.path.join(source_path, task_id))


def get_serial_number(task_id):
    datas = Upload_TestCase.objects.filter(task_id__iregex=r"^%s\d{2}"%task_id).values()
    if len(datas) == 0:
        return "00"
    serials = []
    for data in datas:
        serial = re.search(r'(\d{2})$', data["task_id"]).group(1)
        serials.append(int(serial))


    serial_number = max(serials)+1

    if serial_number >99:
        raise ValueError("Your serial id is gather than 99.")

    max_serial = "%02d" % serial_number

    return max_serial








if __name__ =="__main__":
    modify_task_id("120000","0000")

