import re


# set parameter regex find input id
set_parameter_arg= re.compile(r'arg_([0-9A]+)_(.+)')
set_parameter_other = re.compile(r"^\w+_([0-9A]{6})$")


# modify error message compare
modify_error_message = re.compile(r".+(no valid.+|.+error|.+only allow.+).+")


# form regex
input_task_id = re.compile(r"^[0-2][0-9A]\d{2}$")
input_argument = re.compile(r"[^\w|_]+")





from datetime import datetime
import zipfile
import os
import platform

def archive_folder(task_name):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


    if platform.system() == "Windows":
        file_path = path + r'\upload_folder\\' + task_name
        config_path = path + r"\ait_config\\"

        script_path ="TestScriptRes\\"

    else:
        file_path = path + '/upload_folder/' + task_name
        config_path = path+"/ait_config/"

        script_path = "TestScriptRes/"


    dest_zip ="%s.zip"%datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    zf = zipfile.ZipFile(dest_zip, mode='w')


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


if __name__ =="__main__":

    archive_folder("Check")

