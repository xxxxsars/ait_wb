from django.conf import settings
from django.conf.urls import url, include
from update.views import *
from rest_framework.routers import DefaultRouter
#



urlpatterns = [
    url("^update/(?P<message>.+?)/$",update_index ,name="redirect_update"),
    url("^update/$",update_index ,name="script_update"),
]

