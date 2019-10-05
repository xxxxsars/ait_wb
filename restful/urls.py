from django.conf import settings
from django.conf.urls import url, include
from restful.view import *
from rest_framework.routers import DefaultRouter
#
router = DefaultRouter()
router.register(r'delete', DeleteTestCaseView)
# router.register(r'arg_delete', DeleteArgumentView)

urlpatterns = [
    url("",include(router.urls)),
    url("arg_delete/",DeleteArgumentView)
]

