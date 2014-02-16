from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from journo.views import Map

urlpatterns = patterns('',
    url(r'^$', Map.as_view()),
    url(r'^admin/', include(admin.site.urls)),
)
