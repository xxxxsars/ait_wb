from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect

from update.forms import *

from upload.models import *
from upload.forms import *

from common.limit import modify_error_message




# when redirect will show message to update page
def update_index(request, message=None):
    if request.method == 'POST':
        form = QueryTestCaseForm(request.POST)

        task_id = request.POST["task_id"]
        task_name = request.POST["task_name"]

        if form.is_valid():
            # primary query condition is script_name
            u = UploadFileForm()

            task_info = ""

            if task_name != "":
                task_info = Upload_TestCase.objects.get(task_name=task_name)

            elif task_id != "":
                task_info = Upload_TestCase.objects.get(task_id=task_id)
            task_info = Upload_TestCase.objects.get(task_id=task_id)
            args = Arguments.objects.filter(task_id=task_info)

            return render(request, "modify.html", locals())

    # handle redirect GET request
    form = QueryTestCaseForm()
    if message != None and error_message(message):
        is_error = True

    return render(request, "update.html", locals())




def error_message(message):
    r = modify_error_message
    if r.match( message):
        return True
    return False






