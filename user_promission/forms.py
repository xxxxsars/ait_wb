from django import  forms

from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=40, required=True, label="UserName",
                               error_messages={'required': 'Please enter the UserName', "invalid": "Your UserName had error."})
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"id": "password"}), label="Password",
                               error_messages={"require": 'Please enter the Password', "invalid": "Your Password had error."})

    def clean_username(self):
        self.username=self.cleaned_data['username']

        self.users = []
        for user in User.objects.values_list():
            self.users.append(user[4])

        if self.username not in self.users:
            raise forms.ValidationError("Unrecognized account.")
        return self.username

    def clean_password(self):

        if self.username in self.users:
            vaild = User.check_password(User.objects.get(username=self.username),self.cleaned_data['password'])
            if  not vaild:
                raise forms.ValidationError("Your Password had error.")
            return vaild

