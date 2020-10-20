# -*- coding: utf-8 -*-
'''
Created on 2020/9/30

Author Andy Huang
'''

import os
import re
import json
from common.handler import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django

django.setup()

from test_script.upload.models import *
from project.models import *

class script_parser:
    def __init__(self,content,prj,pn,st):

        self.content = content
        self.prj = prj
        self.pn = pn
        self.st = st

        self.prj_obj = Project.objects.filter(project_name=self.prj)
        self.pn_obj = Project_PN.objects.filter(project_name=self.prj,part_number=self.pn)
        self.st_obj = Project_Station.objects.filter(station_name=self.st,project_pn_id=self.pn_obj[0])
        self.created_prj_task_id = []
        self.task_id = []
        self.ini_content_map = {}
        self.username = self.prj_obj.first().owner_user.username

    def __check_prj(self):

        assert (self.prj_obj.count() >=1) ,"Your project not been created or saved."
        assert (self.pn_obj.count() >=1),"Your project part number not been created or saved ."
        assert (self.st_obj.count()>=1),"Your station not been created or saved."

        prj_task_obj = Project_task.objects.filter(station_id=self.st_obj[0])
        assert (prj_task_obj.count()==0),"Your test case must be empty."


    def __copy_ini(self,task_id):

            path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            lines = [line + '\n' for line in self.content.split("\n") if not re.search(r"^;", line) ]
            content = "".join(lines)

            root_path = handle_path(path, "user_project",self.username,self.prj,self.pn,self.st)

            with open(os.path.join(root_path, "testScript.ini"), "w") as f:
                f.write(content)

            file_info = {"task_list":task_id}

            with open(os.path.join(root_path, "file_info.json"), "w") as f:
                json.dump(file_info,f)

    def __removee_created(self):
        for id in (self.created_prj_task_id):
            prj_task_instance = Project_task.objects.get(id=id)
            prj_task_instance.delete()
            for arg in (Project_task_argument.objects.filter(project_task_id=id)):
                arg.delete()


    def get_task_id(self):
        if not self.task_id:
            self.__removee_created()
            raise Exception("Task id was empty!")

        return self.task_id

    def get_ini_content_map(self):
        if not self.ini_content_map:
            self.__removee_created()
            raise Exception("ini content map was empty!")
        return self.ini_content_map

    def save_prj_task(self,task_type,task_id,task_name,content):
        task_instance = Upload_TestCase.objects.get(task_id=task_id)

        self.task_id.append(task_id)
        inter_type = ["IMAGE","DIALOG","INPUT","INPUTAREA","CONDITIONDIALOG","CMDDIALOG"]

        cmd_reg = re.compile("(cmd|IMAGE|DIALOG|INPUT|INPUTAREA|CONDITIONDIALOG|CMDDIALOG)=(.+)")
        type_map = {}

        priority = ""
        rule = ""
        timeout = 10
        exit_code = "exitCode"
        retry_count = 5
        sleep_time = 0
        cmd = ""

        if task_type =="AUTO":
            inter = "auto"
        else:
            inter = ""

        for line in (content.split("\n")):
            if cmd_reg.match(line):
                g = cmd_reg.search(line)
                content_type = g.group(1)
                if content_type in list(type_map.keys()):
                    err_msg = f"Your testScript.ini the test case id: {task_id} had error."
                    raise Exception (err_msg)
                value = g.group(2)
                type_map[content_type] = value


        assert len(type_map) <= 2, f"Your testScript.ini the test case id: {task_id} had error."

        type_list = [t for t in type_map.keys()  ]


        #get first priority ,which was  cmd or interactive
        if (type_list[0]) !="cmd":
            priority = "interactive"

        #get interactive type
        for t in type_list:
            if t in inter_type:
                inter = t.lower()
                rule = type_map[t]

        assert inter!=""  , f"Your testScript.ini the test case id: {task_id} title had error."

        if "cmd" in type_list:
            content_split = (type_map["cmd"]).split(";")
            try:
                cmd = content_split[0]
                timeout = int(content_split[1])
                exit_code =  content_split[2]
                retry_count =  int(content_split[3])
                sleep_time =  int(content_split[3])
            except Exception as e:
                err_msg = f"Your testScript.ini the test case id: {task_id} get exit_code/retry_count/sleep_time had error."
                raise Exception(err_msg)

        prj_task = Project_task.objects.create(station_id=self.st_obj[0], task_id=task_instance,
                                                  task_name=task_name, timeout=timeout,
                                                  exit_code=exit_code,
                                                  retry_count=retry_count,
                                                  sleep_time=sleep_time, criteria="PASS",
                                                  interactive=inter, rule=rule,
                                                  priority=priority)
        self.created_prj_task_id.append( prj_task.id)



        cmd_split = [ s for s in  re.split("(\".+\")|\s",cmd)  if s][1:]

        arg_obj = Arguments.objects.filter(task_id=task_id)

        if len(cmd_split) != arg_obj.count():
            # Project_task.objects.get(id= prj_task.id).delete()
            err_msg = f"Your testScript.ini the test case id: {task_id} argument not compare database."
            raise Exception(err_msg)


        for i,arg in  enumerate(arg_obj):
            try:
                Project_task_argument.objects.create(default_value=cmd_split[i], argument=arg,
                                                     station_id=self.st_obj.first(), task_id=task_instance,
                                                     project_task_id=prj_task)
            except Exception as e:
                err_msg = f"Your testScript.ini the test case id: {task_id} argument creating error."
                raise Exception(err_msg)


    def convert_script(self):
        self.__check_prj()

        db_task = [ v.task_id  for v in Upload_TestCase.objects.all() ]


        try:
            lines = [line + '\n' for line in self.content.split("\n") if not re.search(r"^;", line) and len(line) > 0]
            content = "".join(lines)
        except Exception as e:
            raise Exception("Read upload testScript.ini failed.")


        scrpit_groups = re.split(r"(\[.+AUTO_\d+.+|INTERACTIVE_\d+.+\])",content)


        if len(scrpit_groups) <= 1 :
            raise Exception("Your testScript.ini had error the parser failed.")

        type_reg = re.compile("^\[.+(AUTO|INTERACTIVE)_(\d+)_([\w|\s]+)\]$")

        content_index = {}

        ini_content = []
        for i,sg in  enumerate( scrpit_groups):
            match = type_reg.search(sg)
            if match:
                content_index[ i+1] =match.group(0)
                task_id = match.group(2)
                if task_id not in db_task:
                    error_msg = f"Your test case id [{task_id}] not match on db"
                    raise Exception(error_msg)


            if i in list(content_index.keys()):

                match_type = type_reg.search(content_index[i])
                scrpit_type = match_type.group(1)
                task_id = match_type.group(2)
                task_name = match_type.group(3)



                parser_content = re.sub("\n$","",re.sub(r"^\n","",sg))

                ini_content.append(content_index[i] +"\n"+parser_content+"\n")

                try:
                    self.save_prj_task(scrpit_type,task_id,task_name,parser_content)
                except Exception as e:
                    self.__removee_created()
                    raise Exception(str(e))

        try:
            order = " ".join([ str(id) for id in self.created_prj_task_id])
            Project_TestScript_order.objects.create(station_name=self.st_obj.first(), part_number=self.pn_obj.first(),
                                                    project_name=self.prj_obj.first(), script_oder=order)
            self.task_id = list(set(self.task_id))
            self.ini_content_map = (dict(zip( self.created_prj_task_id,ini_content)))

            self.__copy_ini(self.task_id)
        except Exception as e:
            self.__removee_created()
            raise Exception(str(e))




#         for id in (self.created_prj_task_id):
#             prj_task_instance = Project_task.objects.get(id=id)
#             prj_task_instance.delete()
#             for arg in (Project_task_argument.objects.filter(project_task_id=id)):
#                 arg.delete()
#
#
#
#
#
# if __name__ =="__main__":
#     with open("/Users/mac/Python/Python_Project/Python/FactoryWeb/common/testScript.ini","r") as fin:
#         lines = fin.read()
#         s = script_parser(lines, "2222222", "DEFAULT", "PCBA_FT1")
#         s.convert_script()
