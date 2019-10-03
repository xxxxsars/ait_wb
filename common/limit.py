import re


# set parameter regex find input id
set_parameter_arg= re.compile(r'arg_([0-9A]+)_(.+)')
set_parameter_other = re.compile(r"^\w+_([0-9A]{6})$")


# modify error message compare
modify_error_message = re.compile(r".+(no valid.+|.+error|.+only allow.+).+")


# form regex
input_task_id = re.compile(r"^[0-2][0-9A]\d{2}$")
input_argument = re.compile(r"[^\w|_]+")






import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django
django.setup()
# from django.core.exceptions import ObjectDoesNotExist
# from django.db.models import Q
from upload.models import *


from datetime import datetime
import zipfile
import os
import platform
import shutil

def archive_folder(task_list):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



    if platform.system() == "Windows":
        config_path = path + r"\ait_config\\"
        dest_path = path +r"\download_folder\\"
        script_path ="TestScriptRes\\"


    else:
        config_path = path+"/ait_config/"
        dest_path = path + "/download_folder/"

        script_path = "TestScriptRes/"



    dest_zip = "%s.zip" % datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    zf = zipfile.ZipFile(os.path.join(dest_path,dest_zip), mode='w')


    for task_name in task_list:
        if platform.system() == "Windows":
            file_path = path + r'\upload_folder\\' + task_name
        else:
            file_path = path + '/upload_folder/' + task_name


        # add source pyfile
        for root, folders, files in os.walk(file_path):
            for sfile in files:
                aFile = os.path.join(root, sfile)
                zf.write(aFile, os.path.join(script_path,os.path.relpath(aFile, file_path)))

    # add default configuration
    for root, folders, files in os.walk(config_path):
        for sfile in files:
            aFile = os.path.join(root, sfile)

            zf.write(aFile,os.path.relpath(aFile, config_path))


    zf.close()






def task_files(task_list):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


    task_files ={}
    for task_name in task_list:
        if platform.system() == "Windows":
            file_path = path + r'\upload_folder\\' + task_name
        else:
            file_path = path + '/upload_folder/' + task_name


        # add source pyfile
        file_list = []
        for root, folders, files in os.walk(file_path):

            for sfile in files:
                aFile = os.path.join(root, sfile)
                file_list.append(os.path.relpath(aFile, file_path))

        task_files[task_name] = file_list

    return task_files



def conflict_files(result_dict):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if platform.system() == "Windows":
        file_path = path + r'\upload_folder\\'
    else:
        file_path = path + '/upload_folder/'

    task_list = []
    for k,v in result_dict.items():
        task_list.append(v["task_name"])


    file_map = task_files(task_list)


    new_files = []

    dedup = []
    for k, fs in file_map.items():
        for f in fs:
            if f in new_files:
                dedup.append(f)
            else:
                new_files.append(f)


    dedup_map = {}
    for k, fs in file_map.items():
        for f in fs:
            if f in dedup:
                dedup_map[k] = os.path.join(os.path.join(file_path,k),f)

    return dedup_map





def detail_error_message(conflict_dict):
    task_list = list(conflict_dict.keys())

    content = 'Your TestCase : "%s" files "%s " had conflict file with TestCase'%(task_list[0]," ,".join(conflict_dict[task_list[0]]))

    for t in task_list[1:]:
        content += ' "%s"'%t

    return content


if __name__ == "__main__":
    di = {'sda': ['json.txt', 'func/1.py'], 'sdf2': ['json.txt', 'func/1.py']}

    detail_error_message(di)