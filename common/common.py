import os
import platform
import re
import shutil
import hashlib

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





if __name__ =="__main__":

    source = "/Users/mac/Python/Python_Project/Python/FactoryWeb/upload_folder/000003/json.txt"

    target = "/Users/mac/Python/Python_Project/Python/FactoryWeb/upload_folder/test/"


    file_copy(source,target)