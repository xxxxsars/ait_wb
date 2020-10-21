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


    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', "rows": "10"}))
    script_name = forms.CharField(max_length=255, required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}),
                                  error_messages={'required': 'Script Name is empty!',
                                                  "invalid": "Please insert valid script name."})

    file = forms.FileField(required=False,
                           widget=forms.FileInput(attrs={'class': 'custom-file-input', "id": "zip_file","accept":".zip"}),
                           error_messages={'required': 'Please update zip file.',
                                           "invalid": "Please update valid zip file"})

    attachment = forms.FileField(widget=forms.FileInput(attrs={'class': 'custom-file-input', "id": "attachment_file","accept":"image/*"}),
                                 required=False)
    def clean_file(self):
        print("in this")
        file = self.cleaned_data.get("file", False)
        if file != None:
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
