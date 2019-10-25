from django.conf.urls import url

from project.views import *

urlpatterns = [
    url("^list/$", list_project, name="list_project"),
    url("^create/$", create_project, name="project_create"),
    url("^select/(?P<project_name>\w{7})/$", select_script, name="select_srcipt"),
    url("^download/(?P<token>\w{30})/$", download, name="export_task"),
    url("^modify/(?P<project_name>\w{7})/$", modify_project, name="project_modify"),
]
