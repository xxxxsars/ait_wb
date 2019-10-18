from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse,Http404
from django.urls import reverse
from upload.models import *



def index(request):
    return render(request,"index.html",locals())