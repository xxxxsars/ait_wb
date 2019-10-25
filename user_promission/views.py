from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import LoginForm

# 將url定義的name轉回網址
from django.urls import reverse

from django.core.mail import send_mail


def login(request):
    login_page = True
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == "POST":

        # 從表單裡取得request裡的Post參數
        f = LoginForm(request.POST)

        # 若表單的所有欄位皆填寫正確，取得裡面的資料
        if f.is_valid():
            #
            username = request.POST['username']
            password = request.POST["password"]
            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return render(request, 'login.html', locals())



    else:
        f = LoginForm()
    return render(request, 'login.html', locals())


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('login'))
