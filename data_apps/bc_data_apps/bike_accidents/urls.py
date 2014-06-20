from django.conf.urls import *

urlpatterns = patterns('data_apps.bc_data_apps.bike_accidents.views',
    url('^get-results/$',               'get_results',      name='bike_accidents_get_results'),
    url('^raw-data/$',                  'raw',              name='bike_accidents_raw'),
    url('^report/$',                    'report',           name='bike_accidents_report'),
    url('^thanks/$',                    'thanks',           name='bike_accidents_thanks'),
    url('^analysis/$',                  'analysis',         name='bike_accidents_analysis'),
    url('^methodology/$',               'methodology',      name='bike_accidents_methodology'),
    url('^charts/$',                    'charts',           name='bike_accidents_charts'),
    url('^$',                           'index',            name='bike_accidents_index'),
)
