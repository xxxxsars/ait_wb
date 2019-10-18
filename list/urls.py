from django.conf import settings
from django.conf.urls import url, include
from list.views import *

urlpatterns = [
    url("^$",index ,name="index"),
    url("^list/$",list_task ,name="list_task"),
    url("^download/",download,name="export_task"),
    url("^test/",confirm,name="test")
]
