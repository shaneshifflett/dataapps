from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bc_data_apps.views.home', name='home'),
    # url(r'^bc_data_apps/', include('bc_data_apps.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^data/bike-accidents/',   include('bc_data_apps.dataapps.bike_accidents.urls')),
    #(r'^immunizations/',    include('bc_data_apps.dataapps.immunizations.urls')),
    #(r'^census-2010/',      include('bc_data_apps.dataapps.census2010.urls')),
    #(r'^mayors-race-2011/', include('bc_data_apps.dataapps.sfmayor2011.urls')),
    #(r'^rankedchoice/',     include('bc_data_apps.dataapps.rankedchoice.urls')),
)
urlpatterns += patterns('',
    (r'^public/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
)
