from django.conf.urls import url

from project.views import *

urlpatterns = [
    url("^save_ini/(?P<token>\w{30})/$", save_ini,name="save_ini"),


    url("^list/$", list_project, name="list_project"),


    url("^create/$", create_project, name="project_create"),
    url("^modify_project/(?P<project_name>\w{7})/$",modify_project),
    url("^modify_project/(?P<project_name>\w{7})/(?P<message>.+)/$",modify_project),


    url("^set_station/(?P<project_name>\w{7})/$",set_station),
    url("^modify_station/(?P<project_name>\w{7})/(?P<part_number>\w+)/$",modify_station),


    url("^select_script/(?P<project_name>\w{7})/(?P<part_number>\w+)/(?P<station_name>\w+)/$", select_script, ),
    url("^modify_script/(?P<project_name>\w{7})/(?P<part_number>\w+)/(?P<station_name>\w+)/$", modify_script, ),
]
