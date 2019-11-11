import os
import platform
import re
import shutil
import hashlib
from common.limit import *
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django

django.setup()

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
        os.makedirs(result_path)

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


from project.views import *






if __name__ == "__main__":
    project_infos = [
        {'task_id': '000001', 'project_task_id': '25', 'script_name': 'sdfdsf.sdf', 'task_name': '0001', 'timeout': '1',
         'exitcode': 'exitCode', 'retry': '3', 'sleep': '0', 'criteria': 'success', 'args': ['01', '111']},
        {'task_id': '000003', 'project_task_id': '29', 'script_name': 'fsdf.sd', 'task_name': 'sdfsdfs11',
         'timeout': '30', 'exitcode': 'exitCode', 'retry': '3', 'sleep': '0', 'criteria': 'success', 'args': []}]

    project_name = "1111111"
    part_number = "DEFAULT"
    station_name = "2222222"








