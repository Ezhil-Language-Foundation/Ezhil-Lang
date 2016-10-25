## (C) 2016 Muthiah Annamalai,
from . import views
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       # evaluate code by enqueuing in file
                       url(r'^eval/$',views.evaluate),

                       # check status of job in queue - (nojob, processing, queued, completed)
                       url(r'^query/?P<job>.+$',views.query),

                       # result of the job
                       url(r'^result/?P<job>.+$',views.result),

                       # delete the job
                       url(r'^delete/?P<job>.+$',views.delete_qjob),
                       )
