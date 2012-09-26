from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView
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
    (r'^data/bike-accidents/',   include('data_apps.bc_data_apps.bike_accidents.urls')),
    (r'^data/immunizations/',    include('data_apps.bc_data_apps.immunizations.urls')),
    (r'^data/census-2010/',      include('data_apps.bc_data_apps.census2010.urls')),
    #(r'^mayors-race-2011/', include('bc_data_apps.dataapps.sfmayor2011.urls')),
    (r'^data/rankedchoice/',     include('data_apps.bc_data_apps.rankedchoice.urls')),
    (r'^data/elections/ca/san-francisco/polling-places', TemplateView.as_view(template_name="elections/poll_loc.html")),
)
urlpatterns += patterns('',
    (r'^public/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
)
