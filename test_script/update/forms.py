from django import forms
from test_script.upload.models import *
import zipfile
from common.limit import input_script_name, input_zip_file_name,input_task_name




class UpdateFileForm(forms.Form):
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

    file = forms.FileField(required=False,
                           widget=forms.FileInput(attrs={'class': 'custom-file-input', "id": "inputGroupFile04"}), )
    def clean_task_name(self):
        task_name = self.cleaned_data['task_name']
        task_id = self.cleaned_data['task_id']

        old_task_name = Upload_TestCase.objects.get(task_id=task_id).task_name

        if task_name !=old_task_name:
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
                'Your Script Name suffix must contains ".py" and name only allow number, letter and underline.')

    def clean_file(self):
        file = self.cleaned_data.get("file", False)
        if file != None:
            if input_zip_file_name.search(str(file)) == None:
                # print("IN")
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
