from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect


import os
import shutil
import platform
import collections

from update.forms import *
from upload.models import *
from upload.forms import *
from common.limit import input_argument,input_default_value



def modify_index(request,task_id):
    u = UpdateFileForm()

    # let js can't dynamic add argument column
    a = ArgumentForm()

    task_info = Upload_TestCase.objects.get(task_id=task_id)
    args = Arguments.objects.filter(task_id=task_info)
    render_value = True


    if request.POST:
        u = UpdateFileForm(request.POST,request.FILES)

        if u.is_valid():
            id = request.POST["task_id"]
            task_name = request.POST["task_name"]
            task_descript = request.POST["task_description"]
            script_name = request.POST["script_name"]


            if  "file" in request.FILES:
                try:
                    handle_update_file(request.FILES['file'], task_name)
                except Exception as e:
                    print("update err",e)
                    error_message = "Upload file is no valid zip file."
                    return render(request, "modify.html", locals())


            # handle post task information
            up =Upload_TestCase.objects.get(task_id=task_id)
            up.script_name = script_name
            up.description = task_descript



            # handle modify argument
            arg_infos = Arguments.objects.filter(task_id=task_info)


            # check ths post data valid
            posted_args = []
            for arg in arg_infos:
                post_arg = request.POST["arg_%s" % arg.argument]
                post_value = request.POST["value_%s" % arg.argument]


                # handle render post value
                if input_argument.search(post_arg) != None:
                    error_message = "Your arguments only allow number, letter and underline."
                    return render(request, "modify.html", locals())

                if post_arg in posted_args:
                    error_message = "Your parameters only allow unique values."
                    return render(request, "modify.html", locals())
                posted_args.append(post_arg)

                if input_default_value.search(post_value) == None:
                    error_message = "Your default value does not match the rule."
                    return render(request, "modify.html", locals())



            # vaild data will be modify
            for arg in arg_infos:
                post_arg = request.POST["arg_%s" % arg.argument]
                post_descript = request.POST["des_%s" % arg.argument]
                post_value = request.POST["value_%s" % arg.argument]

                arg.argument = post_arg
                arg.description = post_descript
                arg.default_value = post_value
                arg.save()


            # handle new argument

            # check if the parameter is a duplicate
            db_args = [i["argument"] for i in arg_infos.values("argument") ]
            new_args = []

            if "argument" and "description" and "default_value" in request.POST:
                descripts = request.POST.getlist("description")
                arguments = request.POST.getlist("argument")
                values = request.POST.getlist("default_value")


                for arg in arguments:
                    if input_argument.search(arg)!=None:
                            error_message = "Your arguments only allow number, letter and underline."
                            return render(request, "modify.html", locals())

                # check new argument not deplicate
                if len( [item for item, count in collections.Counter(arguments).items() if count > 1])>0:
                    error_message = "Your parameters only allow unique values."
                    return render(request, "modify.html", locals())


                for i, e in enumerate(arguments):
                    argument = arguments[i]
                    description = descripts[i]
                    value = values[i]

                    if argument in db_args:
                        error_message = "Your parameters only allow unique values."
                        return render(request, "modify.html", locals())
                    new_args.append(Arguments(argument=argument, description=description, default_value=value,task_id=up))





            # arguments create finish will save the change
            up.save()

            for n_arg in new_args:
                n_arg.save()

            susessful = "Update Test Case ID: [ %s ] was successfully!" % task_id
            # update update value
            task_info = Upload_TestCase.objects.get(task_id=task_id)
            args = Arguments.objects.filter(task_id=task_info)

        else:
            # if not valid display post data
            render_value = False


    return render(request, "modify.html", locals())



# when redirect will show message to update page
def update_index(request, message=None):
    if request.method == 'POST':
        form = QueryTestCaseForm(request.POST)
        task_id = request.POST["task_id"]

        if task_id =="":
            task_name = request.POST["task_name"]
            task_id = Upload_TestCase.objects.get(task_name = task_name).task_id

        if form.is_valid():

            return redirect ("script_modify", task_id)

        else:
            return render(request, "update.html", locals())



    form = QueryTestCaseForm()
    return render(request, "update.html", locals())




# handle_update_file will remove all unzip folder
def handle_update_file(f, task_name):
    if input_zip_file_name.search(str(f.name)) == None:
        raise Exception("Upload file is no valid zip file.")

    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if platform.system() == "Windows":
        source_zip = path + r'\upload_folder\\' + f.name
        unzip_path = path + r'\upload_folder\\'

    else:
        source_zip = path + '/upload_folder/' + f.name
        unzip_path = path + '/upload_folder/'

    with open(source_zip, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # check vaild zip file
    try:
        zip_file = zipfile.ZipFile(source_zip)
        ret = zip_file.testzip()

        if ret is not None:
            raise Exception("not valid zip")
        zip_file.close()
    except Exception:
        os.remove(source_zip)
        raise Exception("Upload file is no valid zip file.")

    # remove old script file
    try:
        shutil.rmtree(unzip_path + task_name)
    except Exception:
        pass

    with zipfile.ZipFile(source_zip, 'r') as zip_ref:
        zip_ref.extractall(unzip_path + task_name)

    os.remove(source_zip)