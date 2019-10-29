import os
import platform
import re


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



