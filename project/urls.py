from django.conf.urls import url

from project.views import *

urlpatterns = [


    url("^download/(?P<token>\w{30})/$", download, name="export_task"),
    url("^modify/(?P<project_name>\w{7})/$", modify_project, name="project_modify"),




    url("^list/$", list_project, name="list_project"),
    url("^create/$", create_project, name="project_create"),
    url("^set_station/(?P<project_name>\w{7})/$",set_station),
    url("^select_script/(?P<project_name>\w{7})/(?P<part_number>\w+)/(?P<station_name>\w+)/$", select_script, ),
]
