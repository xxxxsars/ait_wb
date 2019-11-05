import os
import platform
import re
import shutil
import hashlib

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django
django.setup()


from project.models import *

def handle_path(root_path,*args):
    result_path = ""
    for arg in args:
        if  re.search(r'\.\w+$', arg) !=None:
            raise AttributeError("Your args not allow the file with extension name,only allow folder")
        if result_path =="":
            result_path = os.path.join(root_path,arg)
        else:
            result_path = os.path.join(result_path,arg)
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    return result_path


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_station_instacne(project, part_number, station):
    project_instance = Project.objects.get(project_name=project)
    pn_instance = Project_PN.objects.get(project_name=project_instance, part_number=part_number)
    station_instance = Project_Station.objects.get(project_pn_id=pn_instance, station_name=station)
    return station_instance



def modify_station_name(project_name,part_number,post_st_list):
    project_instance = Project.objects.get(project_name=project_name)
    user_name = project_instance.owner_user.username
    pn_instance = Project_PN.objects.get(project_name=project_instance,part_number=part_number)
    stations = [ s.station_name  for s in Project_Station.objects.filter(project_pn_id=pn_instance)]

    if len(post_st_list) >= len(stations):
        for i,st in enumerate(stations):
            # if not match ,it was be modified
            if st !=post_st_list[i]:
                st_instance = Project_Station.objects.get(project_pn_id=pn_instance,station_name=st)
                st_instance.station_name = post_st_list[i]
                st_instance.save()

                modify_st_folder(user_name,project_name,part_number,st,post_st_list[i])

        for post_st in post_st_list[len(stations):]:
            Project_Station.objects.create(project_pn_id=pn_instance, station_name=post_st)
            create_st_folder(user_name,project_name,part_number,post_st)
    else:
        raise ValueError("Your station name had error.")

def modify_part_number(project_name,post_pn_list):
    project_instance = Project.objects.get(project_name=project_name)
    user_name = project_instance.owner_user.username
    project_pns = [p.part_number for p in Project_PN.objects.filter(project_name=project_instance)]

    if len(post_pn_list)>= len(project_pns):
        for i,pn in enumerate (project_pns):
            if  pn != post_pn_list[i]:
                # if not match ,it was modify
                if post_pn_list[i]!=pn:
                    pn_instance = Project_PN.objects.get(project_name=project_instance,part_number=pn)
                    pn_instance.part_number = post_pn_list[i]
                    pn_instance.save()
                    modify_pn_folder(user_name,project_name,pn,post_pn_list[i])
         # if not in db will create new one
        for post_pn in post_pn_list[len(project_pns):]:
            Project_PN.objects.create(project_name=project_instance,part_number=post_pn)
            create_pn_folder(user_name,project_name,post_pn)

    else:
        raise ValueError("Your part number had error.")



def modify_project_name(old_name,new_name):
    project_instance = Project.objects.get(project_name=old_name)
    pn_instances = Project_PN.objects.filter(project_name=project_instance)
    user_name = project_instance.owner_user.username

    project_instance.project_name = new_name


    project_instance.save()


    for pn in pn_instances:
        pn.project_name= project_instance
        pn.save()

    Project.objects.get(project_name=old_name).delete()

    modify_project_folder(user_name,new_name,old_name)



def modify_project_folder(username,new_name,old_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username)

    old_path = os.path.join(root_path,old_name)
    new_path = os.path.join(root_path,new_name)

    if os.path.exists(new_path):
        os.remove(new_path)

    if not os.path.exists(old_path):
        raise  AttributeError("rename paht %s not existed."%old_path)
    os.rename(old_path,new_path)



def modify_st_folder(username, project_name, part_number,old_name,new_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name,part_number)

    if not os.path.exists(root_path):
        os.makedirs(root_path)

    old_path = os.path.join(root_path,old_name)
    new_path = os.path.join(root_path,new_name)

    if os.path.exists(new_path):
        os.remove(new_path)

    if not os.path.exists(old_path):
        raise  AttributeError("rename paht %s not existed."%old_path)
    os.rename(old_path,new_path)

def create_st_folder(username, project_name, part_number,station_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name,part_number)


    if not os.path.exists(root_path):
        os.makedirs(root_path)

    part_number_path = os.path.join(root_path, station_name)
    if not os.path.exists(part_number_path):
        os.makedirs(part_number_path)



def modify_pn_folder(username, project_name, old_name,new_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name)

    if not os.path.exists(root_path):
        os.makedirs(root_path)

    old_path = os.path.join(root_path,old_name)
    new_path = os.path.join(root_path,new_name)

    if os.path.exists(new_path):
        os.remove(new_path)

    if not os.path.exists(old_path):
        raise  AttributeError("rename paht %s not existed."%old_path)
    os.rename(old_path,new_path)


def create_pn_folder(username, project_name, part_number):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    root_path = handle_path(path, "download_folder", username, project_name)


    if not os.path.exists(root_path):
        os.makedirs(root_path)

    part_number_path = os.path.join(root_path, part_number)
    if not os.path.exists(part_number_path):
        os.makedirs(part_number_path)
if __name__ =="__main__":
    modify_pn_folder("ddd","1231231","DEFAULT","dddddd")


