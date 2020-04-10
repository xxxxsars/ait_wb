from django.conf.urls import include, url
from .views import login, logout

urlpatterns = [
    url(r'^login/$', login, name="login"),
    url('^logout/', logout, name='logout'),
]
