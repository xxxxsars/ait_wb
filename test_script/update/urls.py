from django.conf import settings
from django.conf.urls import url, include
from test_script.update.views import *
from rest_framework.routers import DefaultRouter

urlpatterns = [
    url("^modify/(?P<task_id>\w{6})/$", modify_index_view, name="script_modify"),
    url("^modify/(?P<task_id>\w{6})/(?P<message>.+)/$", modify_index_view,),
    url("update/",update_API_view,name="testCase_update"),

]
