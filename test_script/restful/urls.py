from django.conf import settings
from django.conf.urls import url, include
from test_script.restful.views import *
from rest_framework.routers import DefaultRouter

#
router = DefaultRouter()
router.register(r'delete', DeleteTestCaseView)

urlpatterns = [
    url("", include(router.urls)),
    url("arg_delete/", DeleteArgumentView),
    url("attach_download/(?P<task_id>\w{6})/$",attach_download_view),
    url("script_download/(?P<task_id>\w{6})/$", script_download_view),
    url("delete_attach/$",delete_attachment_view),
    url("vil_cre_name/$",valid_create_script_name_view),
    url("vil_mod_name/$",valid_modify_script_name_view),
    url("vil_script/$",valid_function_view)
]
