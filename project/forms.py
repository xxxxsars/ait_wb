from django import forms

from project.models import *
from common.limit import input_project_name,input_part_station


class CreateProjectForm(forms.Form):
    project_name = forms.CharField(max_length=255, required=True,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   error_messages={'required': 'Project Name is empyt!',
                                                   "invalid": "Please insert valid Project Name"})

    part_number = forms.CharField(max_length=255, required=True,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   error_messages={'required': 'PartNumber is empyt!',
                                                   "invalid": "Please insert valid PartNumber"})

    def clean_project_name(self):
        project_name = self.cleaned_data["project_name"]
        # if Project.objects.filter(project_name=project_name).count():
        #     raise forms.ValidationError("Your Project Name cannot be repeated.Please modify your project name.")


        r = input_project_name
        if r.search(project_name) == None:
            raise forms.ValidationError("Your Project Name not match the Project Name rules.")



    def clean_part_number(self):
        part_number = self.cleaned_data['part_number']

        r = input_part_station

        if r.search(part_number) == None:
            raise forms.ValidationError("Your PartNumber not match the PartNumber rules.")



