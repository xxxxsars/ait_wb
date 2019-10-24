from django import forms
from ait.models import *


class UploadAITForm(forms.Form):
    version = forms.CharField(max_length=255, required=False,widget=forms.TextInput(attrs={'class': 'form-control'}),
                              error_messages={'required': 'Version is empyt!', "invalid": "Please insert valid Version"})
    release_note =forms.CharField( required=False  ,widget=forms.Textarea(attrs={'class': 'form-control' ,"rows":"10" }),
                              error_messages={'required': 'Version is empyt!', "invalid": "Please insert valid Version"})
    file = forms.FileField(required=True,
                           widget=forms.FileInput(attrs={'class': 'custom-file-input', "id": "inputGroupFile04"}),
                           error_messages={'required': 'Please upload AIT file.',
                                           "invalid": "Please upload AIT file"})
