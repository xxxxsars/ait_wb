from django.conf import settings
from django.conf.urls import url, include
from list.views import *

urlpatterns = [
    url("^$",list_index ,name="script_list"),
]
