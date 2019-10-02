from django import forms
import zipfile, re
from upload.models import *

from common.limit import input_task_id,input_argument


class UploadFileForm(forms.Form):
    task_id = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                              error_messages={'required': 'ID is empyt!', "invalid": "Please insert valid ID"})
    task_name = forms.CharField(max_length=255, required=True,
                                     widget=forms.TextInput(attrs={'class': 'form-control'}),
                                     error_messages={'required': 'TestCase Name is empyt!',
                                                     "invalid": "Please insert valid TestCase Name."})
    task_description = forms.CharField(max_length=255, required=True,
                                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    script_name = forms.CharField(max_length=255, required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}),
                                  error_messages={'required': 'Script Name is empty!',
                                                  "invalid": "Please insert valid script name."})

    file = forms.FileField(required=True,
                           widget=forms.FileInput(attrs={'class': 'custom-file-input', "id": "inputGroupFile04"}),
                           error_messages={'required': 'Please update zip file.',
                                           "invalid": "Please update valid zip file"})

    def clean_task_id(self):
        task_id = self.cleaned_data['task_id']
        if Upload_TestCase.objects.filter(task_id=task_id).count():
            raise forms.ValidationError("Your ID cannot be repeated.Please Update it.")

        r = input_task_id
        if r.search(task_id) == None:
            raise forms.ValidationError("Your ID not match the ID rules.")

    def clean_task_name(self):
        task_name = self.cleaned_data['task_name']

        if Upload_TestCase.objects.filter(task_name=task_name).count():
            raise forms.ValidationError("Your TestCase Name cannot be repeated.Please Update it.")

    def clean_file(self):
        file = self.cleaned_data.get("file", False)

        try:
            zip_file = zipfile.ZipFile(file)
            ret = zip_file.testzip()

        except Exception:
            raise forms.ValidationError("Upload file is no valid zip file.")

        if ret is not None:
            raise forms.ValidationError("Upload file is no valid zip file.")

        return file


class ArgumentForm(forms.Form):
    argument = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_argument(self):
        argument = self.cleaned_data['argument']
        r = input_argument
        if r.search(argument) != None:
            raise forms.ValidationError("Your arguments only allow number, letter and underline.")
