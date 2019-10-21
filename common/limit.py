import re




# set parameter regex find input id
set_parameter_arg= re.compile(r'arg_([0-9A]+)_(.+)')
set_parameter_other = re.compile(r"^\w+_([0-9A]{6})$")



# form regex
input_task_id = re.compile(r"^[0-2][0-9A]\d{2}$")
input_task_name = re.compile(r"[^\w|_|\s]+")
input_argument = re.compile(r"[^\w|_]+")


input_project_name = re.compile(r"\w{7}")


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






