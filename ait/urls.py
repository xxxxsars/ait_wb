from django.conf.urls import url

from ait.views import *

urlpatterns = [
    url("^download/$", download_index, name="ait_download"),
    url("^download_file/$", download, name="ait_download_file"),
    url("^release/(?P<version>[\d|\.]+)/$", release_note, name="release_note"),
    url("^upload/$", upload, name="ait_upload"),
    url("^upload_api/$", upload_API, name="upload_api"),

    url("^update/(?P<version>[\d|\.]+)/$", update, name="ait_update"),
    url("^update/(?P<version>[\d|\.]+)/(?P<message>.+)/$", update_message, name="ait_update_message"),
    url("^update_api/$",update_API,name="update_api"),

    url("^valid_version/$",valid_ait_version)

]
