from django.conf.urls import url

from project.views import *

urlpatterns = [
    url("^save_ini/(?P<token>\w{30})/$", save_ini_view,name="save_ini"),


    url("^list/$", list_project_view, name="list_project"),


    url("^create/$", create_project_view, name="project_create"),
    url("^modify_project/(?P<project_name>\w{7})/$",modify_project_view),
    url("^modify_project/(?P<project_name>\w{7})/(?P<message>.+)/$",modify_project_view),


    url("^set_station/(?P<project_name>\w{7})/$",set_station_view),
    url("^modify_station/(?P<project_name>\w{7})/(?P<part_number>\w+)/$",modify_station_view),


    url("^select_script/(?P<project_name>\w{7})/(?P<part_number>\w+)/(?P<station_name>\w+)/$", select_script_view, ),
    url("^modify_script/(?P<project_name>\w{7})/(?P<part_number>\w+)/(?P<station_name>\w+)/$", modify_script_view, ),

    url("^log_confirm/(?P<project_name>\w{7})/$",log_confirm_view),
    url("^upload_log/$",upload_log_view),
]
