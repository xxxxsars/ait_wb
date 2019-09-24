from django import forms
from upload.models import *

class QueryTestCaseForm(forms.Form):
    task_id = forms.CharField(max_length=2551, required=False,widget=forms.TextInput(attrs={'class': 'form-control'}))
    script_name = forms.CharField(max_length=255, required=False,widget=forms.TextInput(attrs={'class': 'form-control'}))



    def clean_task_id(self):
        task_id = self.cleaned_data['task_id']
        self.task_id = task_id
        if task_id!="":
            if Upload_TestCase.objects.filter(task_id=task_id).count()<= 0:
                raise forms.ValidationError("Your provide task id : [%s] is no on record,please upload it."%task_id)

    def clean_script_name(self):

        script_name = self.cleaned_data['script_name']
        self.script_name =script_name
        if script_name!="":
            if Upload_TestCase.objects.filter(script_name=script_name).count() <=0:
                raise forms.ValidationError("Your provide script_name : [%s] is no on record,please upload it."%script_name)
    # todo on js check field
    #
    def clean(self):

    #     # task_id = self.cleaned_data['task_id']
        # script_name = self.cleaned_data['script_name']
        if self.task_id =="" and self.script_name == "":
            raise forms.ValidationError("Your must be provide ID or Script Name to inquire data.")

