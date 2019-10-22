from django.conf.urls import url

from ait.views import *


urlpatterns = [
    url("^download/$",download_index,name="ait_download"),
    url("^download_file/$",download,name="ait_download_file"),
    url("^release/(?P<version>[\d|\.]+)/$",release_note,name="release_note"),
    url("^upload/$",upload,name="ait_upload"),

]