from django.conf import settings
from django.conf.urls import url, include
from update.views import *
from rest_framework.routers import DefaultRouter
#
router = DefaultRouter()
router.register(r'delete', DeleteTestCaseView)



urlpatterns = [
    url("^update/(?P<message>.+?)/$",update_index ,name="redirect_update"),
    url("^update/$",update_index ,name="script_update"),
    url("^modify/$",modify_testCase,name="script_modify"),
    url("",include(router.urls))
]

