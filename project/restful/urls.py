from django.conf import settings
from django.conf.urls import url, include
from project.restful.views import *
from rest_framework.routers import DefaultRouter

#
router = DefaultRouter()
router.register(r'delete', DeleteProjectView)
router.register(r'task_delete', DeleteProjectTaskView)

urlpatterns = [
    url("", include(router.urls)),
    url("pn_delete/$", DeleteProjectPNView),
    url("station_delete/$", DeleteProjectStationView),
    url("get_stored/$", get_script_sorted_view),
    url("modify_user/$", modify_owner_user_view),

    url("download_script/(?P<project_name>\w{7})/(?P<part_number>\w+)/(?P<station_name>\w+)/$",download_view),
    url("upload_script/$", upload_view,name='upload_script'),

    url("valid_project_name/$", valid_projectt_name_view),
    url("valid_part_number/$", valid_part_number_view),

    url("valid_log/$",valid_log_view,name='valid_log'),
    url("keep_station/",keep_station_view,name="keep_station"),
    url("keep_project/",keep_project_view,name="keep_project"),

    url("submit_project/$",submit_project_view,name='submit_project'),

    url("copy_project/$",copy_project_view),
    url("copy_part_number/",copy_part_number_view)

]
