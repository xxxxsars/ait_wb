from django import forms
import zipfile
from test_script.upload.models import *

from common.limit import input_task_id, input_argument, input_script_name, input_zip_file_name, input_task_name, \
    valid_default_value



class PhotoForm(forms.Form):
    task_id = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                              error_messages={'required': 'ID is empyt!', "invalid": "Please insert valid ID"})

    file = forms.FileField(
                           widget=forms.FileInput(attrs={ "id": "fileupload",'class': 'custom-file-input'}),
                           error_messages={'required': 'Please update zip file.',
                                           "invalid": "Please update valid zip file"},required=False)

class UploadFileForm(forms.Form):
    task_id = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                              error_messages={'required': 'ID is empyt!', "invalid": "Please insert valid ID"})
    task_name = forms.CharField(max_length=255, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}),
                                error_messages={'required': 'TestCase Name is empyt!',
                                                "invalid": "Please insert valid TestCase Name."})
    sample = forms.CharField(max_length=255, required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    task_description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', "rows": "10"}))
    script_name = forms.CharField(max_length=255, required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}),
                                  error_messages={'required': 'Script Name is empty!',
                                                  "invalid": "Please insert valid script name."})

    file = forms.FileField(required=True,
                           widget=forms.FileInput(attrs={'class': 'form-control custom-file-input', "id": "zip_file"}),
                           error_messages={'required': 'Please update zip file.',
                                           "invalid": "Please update valid zip file"})

    attachment = forms.FileField(widget=forms.FileInput(attrs={'class': 'custom-file-input', "id": "attachment_file"}),required=False)



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

        r = input_task_name
        if r.search(task_name) != None:
            raise forms.ValidationError("Your TestCase Name only allow number, letter and underline.")

    def clean_script_name(self):
        script_name = self.cleaned_data['script_name']
        r = input_script_name

        if r.search(script_name) == None:
            raise forms.ValidationError(
                'Your Script Name needs to contain a filename extension and the name only allow number, letter and underline.')

    def clean_file(self):
        file = self.cleaned_data.get("file", False)

        if input_zip_file_name.search(str(file)) == None:
            raise forms.ValidationError("Upload file is no valid zip file.")

        try:
            zip_file = zipfile.ZipFile(file)
            ret = zip_file.testzip()

        except Exception:
            raise forms.ValidationError("Upload file is no valid zip file.")

        if ret is not None:
            raise forms.ValidationError("Upload file is no valid zip file.")
        zip_file.close()
        return file


class ArgumentForm(forms.Form):
    argument = forms.CharField(max_length=255, required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(max_length=255, required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))

    default_value = forms.CharField(max_length=255, required=True,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                                    error_messages={'required': 'Default value is empyt!',
                                                    "invalid": "Please insert valid Default Value."})

    def clean_argument(self):
        argument = self.cleaned_data['argument']
        r = input_argument
        if r.search(argument) != None:
            raise forms.ValidationError("Your arguments only allow number, letter and underline.")

    def clean_default_value(self):
        default_value = self.cleaned_data['default_value']
        if valid_default_value(default_value) == False:
            raise forms.ValidationError("Your default value does not match the rule.")
