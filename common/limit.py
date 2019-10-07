import re




# set parameter regex find input id
set_parameter_arg= re.compile(r'arg_([0-9A]+)_(.+)')
set_parameter_other = re.compile(r"^\w+_([0-9A]{6})$")


# modify error message compare
modify_error_message = re.compile(r".+(no valid.+|.+error|.+only allow.+).+")


# form regex
input_task_id = re.compile(r"^[0-2][0-9A]\d{2}$")
input_task_name = re.compile(r"[^\w|_]+")
input_argument = re.compile(r"[^\w|_]+")
input_script_name = re.compile("^[\w|_]+.py$")
input_zip_file_name =  re.compile(r"\.zip$")





import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django
django.setup()
# from django.core.exceptions import ObjectDoesNotExist
# from django.db.models import Q
from upload.models import *





def get_conflict_tasks(conflict_dict):
    # get conflict file
    conflict_files = []
    for k,files in conflict_dict.items():
        for f in files:
            if f in conflict_files:
               pass
            else:
                conflict_files.append(f)


    # get confilct task map by conflict file
    conflict_task = {}
    for cf in conflict_files:
        tasks = []
        for k,files in conflict_dict.items():
            if cf in files:
                tasks.append(k)
        conflict_task[cf] = tasks
    return conflict_task



if __name__ =="__main__":
    conflict_dict = {'test': ['json.txt', 'json1.txt', 'func/1.txt'], 'test2': ['json.txt', '__MACOSX/._json.txt'], 'test3': ['json.txt', '__MACOSX/._json.txt', 'func/1.txt'], 'test4': ['json.txt', 'json1.txt', '__MACOSX/._json.txt']}

