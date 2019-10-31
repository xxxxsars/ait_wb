from django.conf import settings
from django.conf.urls import url, include
from project.restful.views import *
from rest_framework.routers import DefaultRouter

#
router = DefaultRouter()
router.register(r'delete', DeleteProjectView)


urlpatterns = [
    url("", include(router.urls)),
    url("pn_delete/$", DeleteProjectPNView),
]
