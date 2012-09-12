from django.conf.urls.defaults import *

urlpatterns = patterns('data_apps.bc_data_apps.immunizations.views',
    url('^stats-refresh/(?P<from_page>.*?)/$', 'stats_refresh', name='immunizations_stats_refresh'),
    url('^search/$',                           'search',        name='immunizations_search'),
    url('^districts/$',                        'districts',     name='immunizations_districts'),
    url('^districts/(?P<slug>[\w-]+)/$',       'district',      name='immunizations_district'),
    url('^schools/$',                          'schools',       name='immunizations_schools'),
    url('^schools/(?P<slug>[\w-]+)/$',         'school',        name='immunizations_school'),
    url('^cities/$',                           'cities',        name='immunizations_cities'),
    url('^cities/(?P<slug>[\w-]+)/$',          'city',          name='immunizations_city'),
    url('^counties/$',                         'counties',      name='immunizations_counties'),
    url('^counties/(?P<slug>[\w-]+)/$',        'county',        name='immunizations_county'),
    url('^pbe-graph/$',                        'pbe_graph',     name='immunizations_pbe_graph'),
    url('^county-compare-graph/$',             'county_compare_graph',     name='immunizations_county_compare_graph'),
    url('^$',                                  'index',         name='immunizations_index'),
)
