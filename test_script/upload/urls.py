from django.conf import settings
from django.conf.urls import url, include
from test_script.upload.views import *

urlpatterns = [
    url("^create/$", upload_index,name="script_create"),
]

