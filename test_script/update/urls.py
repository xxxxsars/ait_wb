from django.conf import settings
from django.conf.urls import url, include
from test_script.update.views import *
from rest_framework.routers import DefaultRouter

urlpatterns = [
    url("^modify/(?P<task_id>\w{6})/$", modify_index, name="script_modify"),
    url("^modify/(?P<task_id>\w{6})/(?P<message>.+)/$", modify_index,),
]
