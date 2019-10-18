from django.conf import settings
from django.conf.urls import url, include
from list.views import *

urlpatterns = [
    url("^list/",list_task,name="list_script"),
    url("^create/$",create_script ,name="create_srcipt"),
    url("^download/",download,name="export_task"),
    url("^test/",confirm,name="test")
]
