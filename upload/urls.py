from django.conf import settings
from django.conf.urls import url, include
from upload.views import *

urlpatterns = [
    url("^upload/$", upload_index,name="script_upload"),
]

