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
input_default_value = re.compile(r"[^\w|_]+")
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



def conflict_archive_folder(task_list,token,chose_files):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        config_path = path + r"\ait_config\\"
        dest_path = path +r"\download_folder\\"
        script_path ="TestScriptRes\\"
        file_path = path + r'\upload_folder\\'

    else:
        config_path = path+"/ait_config/"
        dest_path = path + "/download_folder/"
        script_path = "TestScriptRes/"
        file_path = path + '/upload_folder/'



    ini_path = os.path.join(dest_path,"%s.ini"%token)

    dest_zip = "%s.zip" % token

    zf = zipfile.ZipFile(os.path.join(dest_path,dest_zip), mode='w')




    chose_files_path = []
    for file, task in chose_files.items():
        chose_files_path.append(os.path.join(os.path.join(file_path, task), file))

    for task_name in task_list:

        source_file_path  = os.path.join(file_path,task_name)
        # add source pyfile
        for root, folders, files in os.walk(source_file_path):
            for sfile in files:
                aFile = os.path.join(root, sfile)
                dest_file = os.path.relpath(aFile, source_file_path)

                if dest_file in list(chose_files.keys()):
                    if aFile in chose_files_path:
                        zf.write(aFile, os.path.join(script_path, dest_file))
                else:

                    zf.write(aFile, os.path.join(script_path,dest_file))

    # add default configuration
    for root, folders, files in os.walk(config_path):
        for sfile in files:
            aFile = os.path.join(root, sfile)

            zf.write(aFile, os.path.relpath(aFile, config_path))

    #add ini
    zf.write(ini_path,"testScript.ini")

    os.remove(ini_path)
    zf.close()



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


