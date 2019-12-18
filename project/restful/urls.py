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
    url("get_stored/$", GetScriptSorted),
    url("modify_user/$", ModifyOwnerUser),
    url("download_script/(?P<project_name>\w{7})/(?P<part_number>\w+)/(?P<station_name>\w+)/$",download),
    url("valid_project_name/$", valid_projectt_name),
    url("valid_log/$",valid_testSCript,name='valid_log'),
    url("submit_project/$",submit_project,name='submit_project')

]
