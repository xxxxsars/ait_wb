from django import forms
from upload.models import *

class QueryTestCaseForm(forms.Form):
    task_id = forms.CharField(max_length=2551, required=False,widget=forms.TextInput(attrs={'class': 'form-control'}))
    task_name = forms.CharField(max_length=255, required=False,widget=forms.TextInput(attrs={'class': 'form-control'}))



    def clean_task_id(self):
        task_id = self.cleaned_data['task_id']
        self.task_id = task_id
        if task_id!="":
            if Upload_TestCase.objects.filter(task_id=task_id).count()<= 0:
                raise forms.ValidationError("Your provide task id : [%s] is no on record,please upload it."%task_id)

    def clean_task_name(self):

        task_name = self.cleaned_data['task_name']
        self.task_name =task_name
        if task_name!="":
            if Upload_TestCase.objects.filter(task_name= task_name).count() <=0:
                raise forms.ValidationError("Your provide TestCase Name : [%s] is no on record,please upload it."%task_name)

    def clean(self):
        if self.task_id =="" and self.task_name == "":
            raise forms.ValidationError("Your must be provide ID or Script Name to inquire data.")

