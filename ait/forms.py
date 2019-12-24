from django import forms
from ait.models import *


class UploadAITForm(forms.Form):
    version = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                              error_messages={'required': 'Version is empyt!',
                                              "invalid": "Please insert valid Version"})
    release_note = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', "rows": "10"}),
                                   error_messages={'required': 'Version is empyt!',
                                                   "invalid": "Please insert valid Version"})
    file = forms.FileField(required=False,
                           widget=forms.FileInput(
                               attrs={'class': 'form-control custom-file-input', "accept": ".jar"}),
                           error_messages={'required': 'Please upload AIT file.',
                                           "invalid": "Please upload valid AIT file"})