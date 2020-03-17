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
import subprocess
from django.forms.models import model_to_dict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django

django.setup()

from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from FactoryWeb.settings import *
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

    root_path = handle_path(path, "user_project", username, project_name)
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    for part_number in part_numbers:
        part_number_path = os.path.join(root_path, part_number)
        if not os.path.exists(part_number_path):
            os.makedirs(part_number_path)


def create_pn_folder(username, project_name, part_number):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "user_project", username, project_name)

    if not os.path.exists(root_path):
        os.makedirs(root_path)

    part_number_path = os.path.join(root_path, part_number)
    if not os.path.exists(part_number_path):
        os.makedirs(part_number_path)


def create_stations_folder(username, project_name, part_number, stations):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "user_project", username, project_name, part_number)
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    for station in stations:
        station_path = os.path.join(root_path, station)
        if not os.path.exists(station_path):
            os.makedirs(station_path)


def create_single_station_folder(username, project_name, part_number, station_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "user_project", username, project_name, part_number)

    if not os.path.exists(root_path):
        os.makedirs(root_path)

    part_number_path = os.path.join(root_path, station_name)
    if not os.path.exists(part_number_path):
        os.makedirs(part_number_path)


def modify_project_folder(username, new_name, old_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "user_project", username)

    old_path = os.path.join(root_path, old_name)
    new_path = os.path.join(root_path, new_name)

    if os.path.exists(new_path):
        os.remove(new_path)

    if not os.path.exists(old_path):
        raise AttributeError("rename paht %s not existed." % old_path)
    os.rename(old_path, new_path)


def modify_station_folder(username, project_name, part_number, old_name, new_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "user_project", username, project_name, part_number)

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

    root_path = handle_path(path, "user_project", username, project_name)

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
    attach_path = os.path.join(handle_path(path, "upload_files", task_id), "attachment")

    if os.path.exists(attach_path):
        return os.listdir(attach_path)[0]
    return ""


def get_modify_time(task_id):
    path = (os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    root_path = handle_path(path, "upload_files", task_id)
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
    project_path = handle_path(path, "user_project", owner_user, project_name, part_number, station_name)
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
            chose_files_path.append(os.path.join(handle_path(path, "upload_files", task_id), file))

    compressed_file = []

    zip_files = []



    for task_id in task_list:
        file_path = handle_path(path, "upload_files", task_id)
        attach_path = handle_path(file_path, "attachment")


        for dirpath, _, filenames in os.walk(file_path):
            for f in filenames:

                full_file_path = os.path.abspath(os.path.join(dirpath, f))
                check_target_path = os.path.relpath(full_file_path, file_path)


                if dirpath != attach_path and check_target_path not in compressed_file:


                    target_path =  os.path.join(script_path,check_target_path)

                    if chose_files != None:
                        # check the file in the conflict files list and add a choose file to the zip file
                        if check_target_path in list(chose_files.keys()):
                            if full_file_path in chose_files_path:
                                zip_files.append((full_file_path, target_path))
                                compressed_file.append(check_target_path)
                    else:

                        zip_files.append((full_file_path,target_path))
                        compressed_file.append(check_target_path)



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


def update_version(version:str) ->str:
    regex = re.compile(r"^(\d){1}\.(\d{2})$")

    matched = regex.search(version)
    if matched:
        first_number = int(matched.group(1))
        second_number = int(matched.group(2))

        if second_number+1 >=99:
            first_number +=1
            second_number = 1

            if first_number >9:
                raise ValueError("Limit number of edits has been exceeded")

        else:
            second_number +=1

        return "%d.%02d"%(first_number,second_number)
    else:
        raise ValueError("Version content is not match")

def samba_mount():
    samba_ip =SAMBA_IP
    account =ACCOUNT
    password = PASSWORD
    share_folder= SAMBA_FOLDER

    win_mount_path =WIN_MOUNT_PATH
    osx_mount_path = OSX_MOUNT_PATH


    mounted = False
    cmd = ""
    if (platform.system() =="Darwin"):
        # check had been mounted
        check_output=  (subprocess.check_output(["mount"])).decode("utf-8")
        if (re.search(r"%s"%osx_mount_path,check_output)):
            # check samba status
            p = subprocess.run( f"smbutil statshares -m {osx_mount_path}".split(" "), timeout=10)
            if p.returncode != 0:
                raise ConnectionError("Connect samba failed.")
            else:
                mounted = True

    elif platform.system() == "Windows":
        # check had been mounted
        check_output = (subprocess.check_output("fsutil fsinfo drives".split(" "))).decode("utf-8")
        if (re.search(r"%s"%win_mount_path,check_output)):
            # check samba status
            p = subprocess.check_output("net use".split(" "), timeout=10)
            result = p.decode("utf-8")
            for i, line in enumerate(result.split("\n")):
                if (re.search(f"{samba_ip}", line)):
                    status = (line.rstrip().split())[0]
                    if status == "OK":
                        mounted = True
                    else:
                        raise ConnectionError("Connect samba failed.")

    if mounted ==False :

        if (platform.system() == "Darwin"):

            cmd = "mount_smbfs //%s:%s@%s/%s %s"%(account,password,samba_ip,share_folder,osx_mount_path)
        elif platform.system() == "Windows":
            cmd = r"net use W: \\%s\%s %s /user:%s" % (samba_ip,share_folder,password,account)

        # wait for 10 second ,if not response will return error
        p = subprocess.check_call(cmd.split(" "),timeout=10)
        if p != 0 :
            raise ConnectionError("Connect samba failed.")

# have modify will disable upload project to AIT server
def disable_upload_project(project_name):
    up_instances = Project_Upload_time.objects.filter(project_name=project_name)
    if up_instances.exists():
        last_instance = up_instances.latest('time')
        last_instance.allow_upload = False
        last_instance.save()

def token_disable_upload_project(token):
    existed = Project_Upload_time.objects.filter(token=token).exists()
    if existed:
        instance = Project_Upload_time.objects.get(token=token)
        instance.allow_upload = False
        instance.save()

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
    try:
        print(update_version("9.99"))
    except ValueError as e:
        print(e)