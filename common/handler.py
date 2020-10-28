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
import zipfile
from rest_framework import authentication
from rest_framework import exceptions
from FactoryWeb.settings import *
from project.models import *
import re
from common.parser import new_script_parser

# handle clare conflicted "common.py" file
def replace_conflict_file():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'upload_folder')
    for dirPath, dirNames, fileNames in os.walk(path):
        for f in fileNames:
            if f == "common.py":
                os.remove(os.path.join(dirPath, f))
                shutil.copyfile("common.txt", os.path.join(dirPath, f))


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
        print("handle_path create new folder", result_path)
        os.makedirs(result_path)

    return result_path


def path_combine(root_path, *args):
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


# old id must be full id ,the new_id only input 4 number
def modify_task_id(old_id, new_id):
    old_instance = Upload_TestCase.objects.filter(task_id=old_id)

    if old_instance.exists() == False:
        raise ValueError("Your provide Task ID had error")

    task_instance = old_instance[0]

    task_name = task_instance.task_name

    id = new_id + get_serial_number(new_id)

    new_task_instance = Upload_TestCase.objects.create(task_id=id,
                                                       task_name="",
                                                       description=task_instance.description,
                                                       script_name=task_instance.script_name)

    arguments_table = Arguments.objects.filter(task_id=task_instance)

    for arg in arguments_table:
        arg.task_id = new_task_instance
        arg.save()

    task_instance.delete()
    new_task_instance.task_name = task_name
    new_task_instance.save()

    # modify the save path
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        source_path = path + r'\upload_files\\'


    else:
        source_path = path + '/upload_files/'

    os.rename(os.path.join(source_path, old_id), os.path.join(source_path, id))


def get_attach_name(task_id):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    attach_path = os.path.join(handle_path(path, "upload_files", task_id), "attachment")

    if os.path.exists(attach_path):
        files =  os.listdir(attach_path)
        if len(files)>0:
            return files[0]

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


def get_download_file(owner_user, project_name, part_number, station_name,script_version):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = handle_path(path, "project", "ait_config")
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
        update_script_version(task_id)
        file_path = handle_path(path, "upload_files", task_id)
        attach_path = handle_path(file_path, "attachment")

        #add interactive images
        if re.search(r"\d(\d{1}).+", task_id).group(1) == "6":
            for dirpath, _, filenames in os.walk(attach_path):
                for f in filenames:
                    full_file_path = os.path.abspath(os.path.join(dirpath, f))
                    zip_files.append((full_file_path, os.path.join("ImageRes",f)))
        else:
            for dirpath, _, filenames in os.walk(file_path):
                for f in filenames:

                    full_file_path = os.path.abspath(os.path.join(dirpath, f))
                    check_target_path = os.path.relpath(full_file_path, file_path)

                    if dirpath != attach_path and check_target_path not in compressed_file:

                        target_path = os.path.join(script_path, check_target_path)

                        if chose_files != None:
                            # check the file in the conflict files list and add a choose file to the zip file
                            if check_target_path in list(chose_files.keys()):
                                if full_file_path in chose_files_path:
                                    zip_files.append((full_file_path, target_path))
                                    compressed_file.append(check_target_path)
                            # append other not conflict files
                            else:
                                zip_files.append((full_file_path, target_path))
                                compressed_file.append(check_target_path)
                        else:

                            zip_files.append((full_file_path, target_path))
                            compressed_file.append(check_target_path)

    if script_version =="new":
        zip_files.append((os.path.join(project_path, "testScript.ini_new"), "testScript.ini"))
    elif script_version =="all":
        zip_files.append((os.path.join(project_path, "testScript.ini_new"), "testScript.ini_new"))
        zip_files.append((os.path.join(project_path, "testScript.ini"), "testScript.ini"))
    else:
        zip_files.append((os.path.join(project_path, "testScript.ini"), "testScript.ini"))

    for root, folders, files in os.walk(config_path):
        for f in files:
            full_file_path = os.path.join(root, f)
            zip_files.append((full_file_path, f))

    # add global script
    for m in [[t.task_id, t.script_name] for t in Upload_TestCase.objects.filter(task_id__iregex=r"^3")]:
        global_script_path = path_combine(path,"upload_files", m[0], m[1])
        target_path = os.path.join(script_path, m[1])
        zip_files.append((global_script_path,target_path))

    return zip_files


def get_keep_files(owner_user, project_name, part_number, station_name,script_version):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_path = path_combine(path, "user_project", owner_user, project_name, part_number, station_name,"keep")

    zip_files = []
    for root, folders, files in os.walk(project_path):
        for f in files:

            # if user select new will ignore testScript.ini
            if script_version =="new" and f =="testScript.ini":
                continue
            #if user select old will ignore testScript.ini_new
            elif script_version =="old" and f =="testScript.ini_new":
                continue

            #change file name
            full_file_path = os.path.join(root, f)
            if "testScript.ini_new" in full_file_path:
                target_path =  re.sub("keep","",os.path.relpath(full_file_path, path_combine(path, "user_project", owner_user)))
                zip_files.append((full_file_path,re.sub("testScript.ini_new","testScript.ini",target_path)))

            else:
                target_path =  re.sub("keep","",os.path.relpath(full_file_path, path_combine(path, "user_project", owner_user)))
                zip_files.append((full_file_path,target_path))

    return zip_files


def get_script_list():
    task_instances = Upload_TestCase.objects.all()
    datas = []
    for instance in task_instances:
        task_map = model_to_dict(instance)
        modify_user = ""
        if instance.modify_user == "":
            modify_user = "-"
        else:
            modify_user = instance.modify_user
        task_map["version"] = "%s [ %s ]" % (instance.version, modify_user)

        arg_instances = Arguments.objects.filter(task_id=instance)

        usage_content = ""
        for arg in arg_instances:
            if re.search("^-\w{1}", arg.default_value) == None:
                usage_content += "-%s\n&nbsp;&nbsp;&nbsp;&nbsp;%s\n" % (arg.argument, arg.description)

        # task_map["useage"] = "Sample:\n%s\n\nUsage:\n%s" % (instance.sample, usage_content)
        task_map["useage"] = "Sample:\n%s"%(instance.sample)
        datas.append(task_map)
    return datas


def get_serial_number(task_id):
    datas = Upload_TestCase.objects.filter(task_id__iregex=r"^%s\d{2}" % task_id).values()
    if len(datas) == 0:
        return "00"
    serials = []
    for data in datas:
        serial = re.search(r'(\d{2})$', data["task_id"]).group(1)
        serials.append(int(serial))

    # if not increment get max serials add 1
    else:
        serial_number = max(serials) + 1

    if serial_number > 99:
        # get not increment the smallest serial number
        tmp = [i for i in range(100)]
        not_increment = []
        for i in tmp[:max(serials)]:
            if i not in serials:
                not_increment.append(i)

        if len(not_increment) != 0:
            serial_number = min(not_increment)
        elif len(not_increment) == 0:
            raise ValueError("Your serial id is gather than 99.")

    serial = "%02d" % serial_number

    return serial



def samba_mount():
    samba_ip = SAMBA_IP
    account = ACCOUNT
    password = PASSWORD
    share_folder = SAMBA_FOLDER

    win_mount_path = WIN_MOUNT_PATH
    osx_mount_path = OSX_MOUNT_PATH

    mounted = False
    cmd = ""
    if (platform.system() == "Darwin"):
        # check had been mounted
        check_output = (subprocess.check_output(["mount"])).decode("utf-8")
        if (re.search(r"%s" % osx_mount_path, check_output)):
            # check samba status
            p = subprocess.run(f"smbutil statshares -m {osx_mount_path}".split(" "), timeout=10)
            if p.returncode != 0:
                raise ConnectionError("Connect samba failed.")
            else:
                mounted = True

    elif platform.system() == "Windows":
        # check had been mounted
        check_output = (subprocess.check_output("fsutil fsinfo drives".split(" "))).decode("utf-8")
        if (re.search(r"%s" % win_mount_path, check_output)):
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

    if mounted == False:

        if (platform.system() == "Darwin"):

            cmd = "mount_smbfs //%s:%s@%s/%s %s" % (account, password, samba_ip, share_folder, osx_mount_path)
        elif platform.system() == "Windows":
            cmd = r"net use W: \\%s\%s %s /user:%s" % (samba_ip, share_folder, password, account)

        # wait for 10 second ,if not response will return error
        p = subprocess.check_call(cmd.split(" "), timeout=10)
        if p != 0:
            raise ConnectionError("Connect samba failed.")


# have modify will disable upload project to AIT server
def disable_upload_project(project_name):
    up_instances = Project_Upload_time.objects.filter(project_name=project_name)
    if up_instances.exists():
        for up in up_instances:
            up.allow_upload = False
            up.save()


def token_disable_upload_project(token):
    existed = Project_Upload_time.objects.filter(token=token).exists()
    if existed:
        instance = Project_Upload_time.objects.get(token=token)
        instance.allow_upload = False
        instance.save()


def valid_zip_file(file, task_id, script_name):
    error_messages = []
    is_modify = True

    instance = Upload_TestCase.objects.filter(task_id=task_id)
    # The existed instance means update files
    if instance.exists():
        version = instance.first().version
    else:
        is_modify = False

    try:
        zip_file = zipfile.ZipFile(file)
        files = zip_file.namelist()


        if re.search(r"^3",task_id):
            invalid_file =[f for f in files if re.search(r"^(.(?<!%s))*$"%script_name,f)]
            if len(invalid_file) >0:
                error_messages.append("Global function only allows one .py file")

        if script_name not in files:
            error_messages.append("Your don't have [%s] file" % script_name)
        elif is_modify:
            version_line = (zip_file.read(script_name)).decode("utf-8").split("\n")[0]
            compare = re.search(r'([\d|\.]+)', version_line)
            if compare == None:
                error_messages.append("Your file not had valid version.")
            else:
                script_version = compare.group(1)
                if script_version != version:
                    error_messages.append("Your script version was not matched.")

        ret = zip_file.testzip()
        if ret is not None:
            error_messages.append("Upload file is no valid zip file.")
        zip_file.close()

    except Exception:
        error_messages.append("Upload file is no valid zip file.")

    return error_messages


def update_script_version(task_id):
    if re.search(r"\d(\d{1}).+", task_id).group(1) == "6":
        return
    task_instance = Upload_TestCase.objects.get(task_id=task_id)
    script_name = task_instance.script_name
    version = task_instance.version

    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(handle_path(path, "upload_files", task_id), script_name)

    if os.path.exists(file_path) == False:
        raise FileNotFoundError(f"[{task_id}] :{file_path} not existed")

    with open(file_path, "r+") as fin:
        lines = fin.readlines()
        version_parameter = f"script_version = \"{version}\"  \n"
        print_version = f"print('script version : {version}')\n"
        try:
            if re.search(r"^#version.+", lines[0]):
                lines[0] = version_parameter
            elif re.search(r"^script_version =.+", lines[0]) == None:
                lines.insert(0, version_parameter)
            else:
                lines[0] = version_parameter
        #if empty file add to top line
        except Exception as e:
            lines.insert(0, version_parameter)
        try:
            if re.search(r"^print\('script version.+", lines[1]) == None:
                lines.insert(1, print_version)
            else:
                lines[1] = print_version
        #if empty file add to second line
        except Exception as e:
            lines.insert(1, print_version)

    with open(file_path, "w") as fout:
        fout.writelines(lines)




def update_ini_version(prj, pn, st):
    prj_instance = Project.objects.get(project_name=prj)
    pn_instance = Project_PN.objects.get(project_name=prj_instance, part_number=pn)
    st_instance = Project_Station.objects.get(project_pn_id=pn_instance, station_name=st)
    owner_user = st_instance.project_pn_id.project_name.owner_user.username
    version = st_instance.version
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_path = handle_path(path, "user_project", owner_user, prj, pn, st)


    ini_path = path_combine(project_path,"testScript.ini")

    try:
        f_ver_reg = re.compile(r"\[FORMAT_VERSION_(\d+)\]")
        t_ver_reg = re.compile(r"\[TESTSCRIPT_VERSION_(.+)\]")
        with open(ini_path,"r") as fin:
            content = fin.read()
            f_match = f_ver_reg.search(content)
            t_match = t_ver_reg.search(content)
            if f_match is None:
                content = ("[FORMAT_VERSION_2]\n\n") +content

            #if had been checked log will append the version
            if version:
                if t_match is None:
                    content = f"[TESTSCRIPT_VERSION_{version}]\n"+content
                elif t_match:
                    content = t_ver_reg.sub(f"[TESTSCRIPT_VERSION_{version}]",content)

        with open(ini_path, "w") as fout:
            fout.write(content)

        s = new_script_parser(ini_path)
        s.convert_script()


    except Exception as e:
        raise  Exception(f"An error occurred while opening the '{ini_path}' file." )




if __name__ == "__main__":

    update_ini_version("9EH3U3L","DEFAULT","PCBA_FT5")










    # station_match_count = 0
    # for index, byte_line in enumerate(lines):
    #     # line = byte_line.decode("utf-8")
    #     line = byte_line
    #     # check station name
    #     station_match = (station_regex.search(line))
    #
    #     if station_match:
    #         station_match_count += 1
    #         log_station = station_match.group(1)
    #         print(log_station)
            # if log_station != station_name:
            #     token_disable_upload_project(token)
            #     return JsonResponse({"valid": False, "message": "The log file station name not compared."}, status=400)

        # check log the all task was passed
    #     matched = valid_reg.search(line)
    #
    #     if matched:
    #         if matched.group(2) == "PASS":
    #             # add pass task name to list
    #             task_names.append((matched.group(1).strip()))
    #             task_id_line_inedx.append(index + 1)
    #
    #         else:
    #             token_disable_upload_project(token)
    #             return JsonResponse(
    #                 {"valid": False, "message": "The testCase '%s' was failed." % matched.group(1).strip()}, status=400)
    #
    #     if index in task_id_line_inedx:
    #         # add pass task id to list
    #         test_id_match = test_id_regex.search(line)
    #         if test_id_match:
    #             task_ids.append(test_id_match.group(1))
    #
    # if station_match_count <= 0:
    #     token_disable_upload_project(token)
    #     return JsonResponse({"valid": False, "message": "Can't find log station name."}, status=400)
    #
    # # check testScript order
    # task_id_map = {p.id: p.task_name for p in Project_task.objects.filter(station_id=station_instance)}
    # sort_task_name_id = Project_TestScript_order.objects.get(station_name=station_instance).script_oder.split(" ")
    #
    # for id in sort_task_name_id:
    #     compare_task_name.append((task_id_map[int(id)]).strip())
    #
    # # check testCase id
    # compare_task_id = [instance.task_id.task_id for instance in
    #                    Project_task.objects.filter(station_id=station_instance)]
    #
    # # check task name
    # if task_names == compare_task_name:
    #
    #     # check task id
    #     sort_compare_task_id = [int(i) for i in compare_task_id]
    #     sort_task_ids = [int(i) for i in task_ids]
    #
    #     sort_compare_task_id.sort()
    #     sort_task_ids.sort()
    #     if sort_compare_task_id == sort_task_ids:
    #         # create log pass message to project_upload_time and set "allow_upload" to the "True"
    #         # only all upload but not had been uploaded to samba so the username was "none"
    #         instance, created = Project_Upload_time.objects.get_or_create(token=token, project_name=Project.objects.get(
    #             project_name=project_name))
    #         instance.allow_upload = True
    #         instance.save()
    #
    #         return JsonResponse({"valid": True, "message": "The log file was passed."})
    # else:
    #
    #     token_disable_upload_project(token)
    #     return JsonResponse({"valid": False, "message": "Please re-download this testScript and test it aging."},
    #                         status=400)

