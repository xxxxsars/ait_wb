# -*- coding: utf-8 -*-
'''
Created on 2020/9/30

Author Andy Huang
'''

import os
import re
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactoryWeb.settings')
import django

django.setup()

from test_script.upload.models import *
from project.models import *

class upload_script_parser:
    def __init__(self,content,prj,pn,st):

        self.content = content
        self.prj = prj
        self.pn = pn
        self.st = st


        self.created_prj_task_id = []
        self.task_id = []
        self.ini_content_map = {}


    def __check_prj(self):
        self.prj_obj = Project.objects.filter(project_name=self.prj)
        assert (self.prj_obj.count() >= 1), "Your project has not been created or saved."
        self.pn_obj = Project_PN.objects.filter(project_name=self.prj,part_number=self.pn)
        assert (self.pn_obj.count() >= 1), "Your project part number has not been created or saved ."
        self.st_obj = Project_Station.objects.filter(station_name=self.st,project_pn_id=self.pn_obj[0])
        assert (self.st_obj.count()>=1),"Your station has not been created or saved."

        prj_task_obj = Project_task.objects.filter(station_id=self.st_obj[0])
        assert (prj_task_obj.count()==0),"Your test case must be empty."

        self.username = self.prj_obj.first().owner_user.username

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

        for order in  Project_TestScript_order.objects.filter(station_name=self.st_obj.first(), part_number=self.pn_obj.first(),
                                                    project_name=self.prj_obj.first()):
            order.delete()

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

        # print(task_type,task_id,task_name,content)

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


        if re.search(r"^\d6",task_id) == None:
            assert len(type_map) > 0, f"Your testScript.ini the test case id: {task_id} had error."

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
        cmd_split = [ s for s in  re.split('''('.*?'|".*?"|\S+)''',cmd)  if re.search("\w",s)][1:]
        arg_obj = Arguments.objects.filter(task_id=task_id)

        # check parameter
        if len(cmd_split) > arg_obj.count():
            err_msg = f"Your testScript.ini the test case id: {task_id} has more parameters than the database."
            raise Exception(err_msg)

        key_value_arg = [a.default_value for a in arg_obj if re.match(r"^-.+", a.default_value) and re.match(r"_.+", a.argument)]

        if key_value_arg:
            if len(cmd_split)%2:
               err_msg = f"Your testScript.ini the test case id: {task_id} with key-value parameters does not match the database."
               raise Exception(err_msg)
            #if key-value parameter was empty will append the empty value
            else:
                # print(task_id,cmd_split, [a.default_value for a in arg_obj])
                for i,arg in enumerate( [a.default_value for a in arg_obj]):
                    if re.match(r"^-.+",arg):
                        try:
                            cmd_split[i]
                        except Exception as e:
                            cmd_split.insert(i, arg)
                            cmd_split.insert(i + 1, "")

                        if (arg != cmd_split[i]):
                            cmd_split.insert(i,arg)
                            cmd_split.insert(i+1,"")

            # if convert the cmd_split ,it count must compare the db argument count.
            assert len(cmd_split) == arg_obj.count(), f"Your testScript.ini the test case id: {task_id} parameters does not match the database."

        #if not key-value parameter and cmd paramters less than db will ingore some parameters
        if len(cmd_split) < arg_obj.count():
            arg_obj= arg_obj[:len(cmd_split)]



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


        # check testScript version
        for line in lines:
            match = re.search(r"\[FORMAT_VERSION_(\d+)\]", line)
            if match:
                if match.group(1) == "2":
                    raise Exception("TestScript.ini version 2 not support upload.")

        scrpit_groups = re.split(r"(\[.+\])",content)

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
                    self.__removee_created()
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
                    # print(scrpit_type,task_id,task_name,parser_content)
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


        # todo :remove it
        self.__removee_created()



class new_script_parser:
    def __init__(self,path:str):

        #Define the cmd index
        self.__CMD = 0
        self.__TIMEOUT = 1
        self.__CMD_CONDITION =2
        self.__RETRY = 3
        self.__SLEEP = 4
        self.__RETRY_WAIT = 5

        #Define the interactive index
        self.__TITLE = 0
        self.__CONTENT = 1
        self.__LINES = 2
        self.__IMAGE = 3
        self.__INTER_CONDITION = 4

        #Initial in / out streaming
        self.path = path
        self.fin = open(path,'r')
        self.fout =  open(path+"_new",'w')

    def __del__(self):
        self.fin.close()
        self.fout.close()


    def __convert_cmd(self,type:str,value:str):

        result = ""
        cut_cmd = value.split(";")
        try:
            cmd =  re.sub( '"',"'" ,cut_cmd[self.__CMD])
            timeout = cut_cmd[self.__TIMEOUT]
            condition = cut_cmd[self.__CMD_CONDITION]
            retry = cut_cmd[self.__RETRY]
            sleep = cut_cmd[self.__SLEEP]
        except Exception as e:
            raise Exception("Cut command had error:"+str(e))


        if type=="AUTO":
            result += "CMD=" + cmd +"\n"
            result += "TIMEOUT=" + timeout+ "\n"
            result += "CONDITION=" + condition + "\n"
            result += "RETRY=" + retry +"\n"
            result += "SLEEP=" + sleep
        elif type == "INTERACTIVE":

            result_json = {"CMD":cmd,"TIMEOUT":timeout,"CONDITION":condition,"RETRY":retry,"SLEEP":sleep}
            if len(cut_cmd) >5:
                result_json["RETRY_WAIT"] = cut_cmd[self.__RETRY_WAIT]
            result = "CMD=" + json.dumps(result_json)

        return result

    def __convert_interactive(self,type:str,value:str):

        try:
            result = ""
            cut_cmd = value.split(";")
            result += "TITLE=" + cut_cmd[self.__TITLE] +"\n"
            result += "CONTEXT=" + cut_cmd[self.__CONTENT]+ "\n"

            if type == "INPUTAREA":
                result += "LINES=" + cut_cmd[self.__LINES] + "\n"
            elif type =="DIALOG":
                result += "CONDITION=Y"

            if (len(cut_cmd)>=4):
                if cut_cmd[self.__IMAGE]:
                    result += "IMAGE=" + cut_cmd[self.__IMAGE] + "\n"
                if type == "CONDITIONDIALOG":
                    result += "CONDITION=" + cut_cmd[self.__INTER_CONDITION] + "\n"
                elif type=="IMAGE":
                    result += "CONDITION=Y"


        except Exception as e:
            raise Exception("Convert interactive test case had error:"+str(e))

        result = re.sub("\n$", "", result)

        return result

    def convert_script(self):
        try:
            content = self.fin.read()
            lines = content.split("\n")
        except Exception as e:
            raise Exception("Your old testScript.ini was empty.")

        f_ver_reg = re.compile(r"\[FORMAT_VERSION_(\d+)\]")
        scrpit_groups = re.split(r"\[.+(AUTO|INTERACTIVE).+\]",content)
        cmd_reg =re.compile("(cmd|IMAGE|DIALOG|INPUT|INPUTAREA|CONDITIONDIALOG|CMDDIALOG)=(.+)")

        convert_map = []

        content_index = {}
        for i,sg in  enumerate( scrpit_groups):
            if re.search("^(AUTO|INTERACTIVE)$",sg):
                content_index[ i+1] =sg

            if i in list(content_index.keys()):
                scrpit_type = content_index[i]

                for line in  sg.split("\n"):

                    if cmd_reg.match(line):
                        trans_result = {"origin":line}
                        g = cmd_reg.search(line)
                        content_type = g.group(1)
                        value = g.group(2)

                        # print(content_type, value)
                        if content_type =="cmd":
                            trans_result["convert"] = self.__convert_cmd(scrpit_type,value)
                        else:
                            trans_result["convert"] = self.__convert_interactive(content_type,value)
                        convert_map.append(trans_result)

        # write to  file
        for line in lines:
            for map in convert_map:
                # if the line compare the map ,will convert to new line
                if line == map["origin"]:
                    line = (map["convert"])
            else:
                # criteria will ignore it
                if re.search("^criteria.+",line):
                    line =""

                #replace format to ver.2
                if f_ver_reg.search(line):
                    line = f_ver_reg.sub("[FORMAT_VERSION_2]",line)
                self.fout.write(line+"\n")



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