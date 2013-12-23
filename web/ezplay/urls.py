## (C) 2013 Muthiah Annamalai,
from django.conf.urls import patterns, include, url
from django.shortcuts import render_to_response

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       # dynamic views

                       # evaluate code/provide the form
                       url(r'^eval/?$'views.evaluate),
                       
                       # save code received as a post form.
                       url(r'^save/?P<prefix>.+$',views.save),

                       # download the code given a snippet
                       url(r'^download/?P<prefix>.+$',views.download),
                       
                       # view recently saved snippets
                       # url(r'^recent',views.recent),

                       # view recently snippet previously saved
                       url(r'^lookup/?P<prefix>.+$',lambda x: views.lookup),
                       )
