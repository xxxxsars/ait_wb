from django.conf.urls import url

from project.views import *


urlpatterns = [
    url("^create/$",create_project_index,name="project_create"),
    url("^select/(?P<project_name>\w{7})/$",select_script ,name="select_srcipt"),
    url("^download//(?P<token>\w{30})/$", download, name="export_task"),
]