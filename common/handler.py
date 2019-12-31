import os
import platform
import re
import shutil
import time
import hashlib
from common.limit import *
import os
import json
import socket
from django.forms.models import model_to_dict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django

django.setup()

from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

from project.models import *

def handle_path(root_path, *args):
    result_path = ""
    for arg in args:
        if re.search(r'\.\w+$', arg) != None:
            raise AttributeError("Your args not allow the file with extension name,only allow folder")
        if result_path == "":
            result_path = os.path.join(root_path, arg)
        else:
            result_path = os.path.join(result_path, arg)
    if not os.path.exists(result_path):
        print("handle_path create new folder",result_path)
        os.makedirs(result_path)

    return result_path


def path_combine(root_path,*args):
    result_path = ""
    for arg in args:
        if result_path == "":
            result_path = os.path.join(root_path, arg)
        else:
            result_path = os.path.join(result_path, arg)
    return result_path

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def create_project_folder(username, project_name, part_numbers):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name)
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    for part_number in part_numbers:
        part_number_path = os.path.join(root_path, part_number)
        if not os.path.exists(part_number_path):
            os.makedirs(part_number_path)


def create_pn_folder(username, project_name, part_number):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name)

    if not os.path.exists(root_path):
        os.makedirs(root_path)

    part_number_path = os.path.join(root_path, part_number)
    if not os.path.exists(part_number_path):
        os.makedirs(part_number_path)


def create_stations_folder(username, project_name, part_number, stations):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name, part_number)
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    for station in stations:
        station_path = os.path.join(root_path, station)
        if not os.path.exists(station_path):
            os.makedirs(station_path)


def create_single_station_folder(username, project_name, part_number, station_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name, part_number)

    if not os.path.exists(root_path):
        os.makedirs(root_path)

    part_number_path = os.path.join(root_path, station_name)
    if not os.path.exists(part_number_path):
        os.makedirs(part_number_path)


def modify_project_folder(username, new_name, old_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username)

    old_path = os.path.join(root_path, old_name)
    new_path = os.path.join(root_path, new_name)

    if os.path.exists(new_path):
        os.remove(new_path)

    if not os.path.exists(old_path):
        raise AttributeError("rename paht %s not existed." % old_path)
    os.rename(old_path, new_path)


def modify_station_folder(username, project_name, part_number, old_name, new_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name, part_number)

    if not os.path.exists(root_path):
        os.makedirs(root_path)

    old_path = os.path.join(root_path, old_name)
    new_path = os.path.join(root_path, new_name)

    if os.path.exists(new_path):
        os.remove(new_path)

    if not os.path.exists(old_path):
        raise AttributeError("rename paht %s not existed." % old_path)
    os.rename(old_path, new_path)


def modify_pn_folder(username, project_name, old_name, new_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name)

    if not os.path.exists(root_path):
        os.makedirs(root_path)

    old_path = os.path.join(root_path, old_name)
    new_path = os.path.join(root_path, new_name)

    if os.path.exists(new_path):
        os.remove(new_path)

    if not os.path.exists(old_path):
        raise AttributeError("rename paht %s not existed." % old_path)
    os.rename(old_path, new_path)


def get_attach_name(task_id):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    attach_path = os.path.join(handle_path(path, "upload_folder", task_id), "attachment")

    if os.path.exists(attach_path):
        return os.listdir(attach_path)[0]
    return ""


def get_modify_time(task_id):
    path = (os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    root_path = handle_path(path, "upload_folder", task_id)
    updata_file_path = ""
    for file in os.listdir(root_path):
        if file != "attachment" and re.search("^\.", file) == None:
            file_path = os.path.join(root_path, file)
            updata_file_path = file_path
            # get first file
            break
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(updata_file_path)))


def get_download_file(owner_user, project_name, part_number, station_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = handle_path(path, "ait_config")
    project_path = handle_path(path, "download_folder", owner_user, project_name, part_number, station_name)
    json_file = os.path.join(project_path, "file_info.json")
    script_path = "TestScriptRes"

    json_data = json.load(open(json_file, 'r'))

    task_list = json_data['task_list']
    chose_files = None
    if "chose_file" in json_data:
        chose_files = json_data['chose_file']
    chose_files_path = []
    if chose_files != None:
        for file, task_id in chose_files.items():
            chose_files_path.append(os.path.join(handle_path(path, "upload_folder", task_id), file))

    compressed_file = []

    zip_files = []

    for task_id in task_list:
        file_path = handle_path(path, "upload_folder", task_id)
        attach_path = handle_path(file_path, "attachment")
        for root, folders, files in os.walk(file_path):
            for f in files:
                # ignore attachment path
                if root != attach_path:
                    if f not in compressed_file:
                        full_file_path = os.path.join(root, f)
                        # remove unless path  prefix
                        dest_copy_file = os.path.relpath(full_file_path, file_path)
                        dest = os.path.join(script_path, os.path.dirname(dest_copy_file))

                        # if had conflicted files will only copy chose files.
                        if chose_files != None:
                            if dest_copy_file in list(chose_files.keys()):
                                if full_file_path in chose_files_path:
                                    zip_files.append(
                                        (full_file_path, os.path.join(dest, (os.path.basename(dest_copy_file)))))
                            elif f not in compressed_file:
                                zip_files.append(
                                    (full_file_path, os.path.join(dest, (os.path.basename(dest_copy_file)))))
                                compressed_file.append(f)

                        # if did not have conflict_files will coop all task file to user folder
                        else:
                            # create the dest file path
                            zip_files.append(
                                (full_file_path, os.path.join(dest, (os.path.basename(dest_copy_file)))))
                            compressed_file.append(f)


    zip_files.append((os.path.join(project_path,"testScript.ini"),"testScript.ini"))
    for root, folders, files in os.walk(config_path):
        for f in files:
            full_file_path = os.path.join(root, f)
            zip_files.append((full_file_path, f))

    return zip_files



def get_script_list():
    task_instances = Upload_TestCase.objects.all()
    datas = []
    for instance in task_instances:
        task_map = model_to_dict(instance)
        modify_user = ""
        if instance.modify_user =="":
            modify_user = "-"
        else:
            modify_user = instance.modify_user
        task_map["version"] = "%s [ %s ]"%(instance.version,modify_user)

        arg_instances = Arguments.objects.filter(task_id=instance)

        usage_content  = ""
        for arg in arg_instances:
            if re.search("^-\w{1}",arg.default_value) ==None:
                usage_content += "-%s\n&nbsp;&nbsp;&nbsp;&nbsp;%s\n"%(arg.argument,arg.description)

        task_map["useage"] = "Sample:\n%s\n\nUsage:\n%s"%(instance.sample,usage_content)
        datas.append(task_map)
    return datas

if __name__ =="__main__":
    # import shutil
    #
    # path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'upload_folder')
    # for dirPath, dirNames, fileNames in os.walk(path):
    #     for f in fileNames:
    #         if f == "common.py":
    #             print(os.path.join(dirPath, f))
    #             os.remove(os.path.join(dirPath, f))
    #             shutil.copyfile("common.txt",os.path.join(dirPath, f))

    li = [{'id': 85, 'station_id': 18, 'task_id': '060001', 'task_name': 'Check project name', 'timeout': 10, 'exit_code': 'exitCode', 'retry_count': 5, 'sleep_time': 0, 'criteria': '', 'args': [{'id': 327, 'default_value': '"HP Elite USB-C Multi Port Hub"', 'argument': 'Project_Name', 'task_id': '060001', 'description': 'The project caption'}], 'project_description': 'Description:<br>[1]Product connection Host \r\n[2]Compare caption names for consistency<br><br>Sample:<br>Check_project_caption.py "HP Elite USB-C Multi Port Hub"'}, {'id': 87, 'station_id': 18, 'task_id': '000000', 'task_name': 'CHECK BRIDGE FW', 'timeout': 10, 'exit_code': 'exitCode', 'retry_count': 5, 'sleep_time': 0, 'criteria': '', 'args': [{'id': 329, 'default_value': 'pcba', 'argument': 'function_name', 'task_id': '000000', 'description': 'pcba/bridge'}], 'project_description': 'Description:<br>check bridge firmware<br><br>Sample:<br>TestScriptRes\\CHECK_BRIDGE_FW.py -f pcba'}, {'id': 88, 'station_id': 18, 'task_id': '000001', 'task_name': 'EDA9015 VOLTAGE TEST', 'timeout': 10, 'exit_code': 'exitCode', 'retry_count': 5, 'sleep_time': 0, 'criteria': '', 'args': [{'id': 330, 'default_value': 'COM6', 'argument': 'COM_PORT', 'task_id': '000001', 'description': 'Check com port on device management'}], 'project_description': 'Description:<br>[1]Check com port on device management\r\n[2]Modify the spec of test point that provided by hardware \r\n[3]Check voltage of testing point with EDA9015<br><br>Sample:<br>TestScriptRes\\EDA9015_VOLTAGE_TEST.py COM6'}, {'id': 89, 'station_id': 18, 'task_id': '000000', 'task_name': 'CHECK BRIDGE FW', 'timeout': 10, 'exit_code': 'exitCode', 'retry_count': 5, 'sleep_time': 0, 'criteria': '', 'args': [{'id': 331, 'default_value': 'pcba', 'argument': 'function_name', 'task_id': '000000', 'description': 'pcba/bridge'}], 'project_description': 'Description:<br>check bridge firmware<br><br>Sample:<br>TestScriptRes\\CHECK_BRIDGE_FW.py -f pcba'}]

    for i in li:
        for k ,v  in (i.items()):
            print(k,":",v)