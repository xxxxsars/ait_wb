from django import forms
import zipfile
from upload.models import *

class UploadFileForm(forms.Form):
    task_id =  forms.CharField(max_length=2551,widget=forms.TextInput(attrs={'class' : 'form-control'}),error_messages={'required':'ID is empyt!',"invalid":"Please insert valid ID"})
    script_name =  forms.CharField(max_length=255,required = True,widget=forms.TextInput(attrs={'class' : 'form-control'}),error_messages={'required':'Script Name is empty!',"invalid":"Please insert valid script name."})

    description =  forms.CharField(max_length=255,widget=forms.TextInput(attrs={'class' : 'form-control'}))
    exec_time =  forms.IntegerField(required = True,widget=forms.TextInput(attrs={'class' : 'form-control'}),error_messages={'required':'Exec time is empty!',"invalid":"Please insert valid Exec time."})
    argument =  forms.CharField(max_length=255,required = True,widget=forms.TextInput(attrs={'class' : 'form-control'}),error_messages={'required':'Argument field is empty!',"invalid":"Please insert valid ID"})
    file = forms.FileField(required = True,widget=forms.FileInput(attrs={'class' : 'custom-file-input',"id":"inputGroupFile04"}),error_messages={'required':'Please update zip file.',"invalid":"Please update valid zip file"})


    def clean_task_id(self):
        task_id = self.cleaned_data['task_id']
        if Upload_TestCase.objects.filter(task_id=task_id).count():
            raise forms.ValidationError("Your ID cannot be repeated.Please Update it.")


    def clean_script_name(self):
        script_name = self.cleaned_data['script_name']
        if Upload_TestCase.objects.filter(script_name=script_name).count():
            raise forms.ValidationError("Your Script Name cannot be repeated.Please Update it.")


    def clean_file(self):
        file = self.cleaned_data.get("file",False)

        try :
            zip_file = zipfile.ZipFile(file)
            ret = zip_file.testzip()

        except Exception:
            raise forms.ValidationError("Upload file is no valid zip file.")

        if ret is not None:
            raise forms.ValidationError("Upload file is no valid zip file.")

        return file