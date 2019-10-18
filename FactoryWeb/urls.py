"""FactoryWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
from FactoryWeb import settings
from .error_views import *
from django.views.static import serve
from FactoryWeb.view import *

urlpatterns = [
    url('admin/', admin.site.urls),
    url("^$",index,name="index"),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    url("^testCase/",include("test_script.upload.urls")),
    url("^testCase/",include("test_script.update.urls")),
    url("^testCase/",include("restful.urls")),
    url("^testCase/", include("test_script.list.urls")),
    url("^user/",include("user_information.urls")),

]


if settings.DEBUG==False:
    handler404 = error_404

    handler500 = error_500
