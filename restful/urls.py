from django.conf import settings
from django.conf.urls import url, include
from restful.view import *
from rest_framework.routers import DefaultRouter
#
router = DefaultRouter()
router.register(r'delete', DeleteTestCaseView)


urlpatterns = [
    url("",include(router.urls)),
    url("arg_delete/",DeleteArgumentView)
]

