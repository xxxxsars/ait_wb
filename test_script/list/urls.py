from django.conf import settings
from django.conf.urls import url, include
from test_script.list.views import *

urlpatterns = [
    url("^list/",list_task,name="list_script"),
    url("^test/",confirm,name="test")
]
