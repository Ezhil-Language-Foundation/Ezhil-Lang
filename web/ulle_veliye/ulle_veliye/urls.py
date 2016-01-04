"""ulle_veliye URL Configuration
"""
from django.conf.urls import include, url
from django.contrib import admin
from api.views import api_view

urlpatterns = [
    url(r'^api/$', api_view, name='api-view'),
    url(r'^admin/', include(admin.site.urls)),
]
