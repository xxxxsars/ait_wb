import re




# set parameter regex find input id
set_parameter_arg= re.compile(r'arg_([0-9A]+)_(.+)')
set_parameter_other = re.compile(r"^\w+_([0-9A]{6})$")



# form regex
input_task_id = re.compile(r"^[0-2][0-9A]\d{2}$")
input_task_name = re.compile(r"[^\w|_]+")
input_argument = re.compile(r"[^\w|_]+")
input_default_value = re.compile(r'(^"(\w+\s+\w+)"$)|^(\w+\.*\w+)+$|^\w+$')
input_script_name = re.compile("^[\w|_]+.py$")
input_zip_file_name =  re.compile(r"\.zip$")





import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django
django.setup()
# from django.core.exceptions import ObjectDoesNotExist
# from django.db.models import Q
from upload.models import *

import platform,os,zipfile



def valid_default_value(value):
    pass


if __name__ =="__main__":

    # path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #
    # if platform.system() == "Windows":
    #     file_path = path + r'\upload_folder\\'
    # else:
    #     file_path = path + '/upload_folder/'
    #
    #
    chose_map = {'json.txt': 'test2', 'json1.txt': 'test', '__MACOSX/._json.txt': 'test2'}
    #
    #
    # chose_files_path = []
    # for file,task in chose_map.items():
    #     chose_files_path.append( os.path.join(os.path.join(file_path,task),file))
    #
    #
    # print(list(chose_map.keys()))

    conflict_archive_folder(["test","test2"],"HGpi8kVZsgPKoNTuA3h82n44lLrkJG",chose_map)


