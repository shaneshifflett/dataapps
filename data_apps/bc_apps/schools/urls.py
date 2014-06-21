from django.conf.urls import patterns, url

urlpatterns = patterns('schools.views',
    url('^districts/district/(?P<slug>.*?)/(?P<show>.*?)/$',    'districts_view',   name='schools_districts_view_show'),
    url('^districts/district/(?P<slug>.*?)/$',                  'districts_view',   name='schools_districts_view'),
    url('^districts/(?P<show>.*?)/$',                           'districts_index',  name='schools_districts_index_show'),
    url(r'^districts/$',                                        'districts_index',  name='schools_districts_index'),
    url('^school/(?P<slug>.*?)/(?P<show>.*?)/$',                'view',             name='schools_view_show'),
    url('^school/(?P<slug>.*?)/$',                              'view',             name='schools_view'),
    url('^(?P<show>.*?)/$',                                     'index',            name='schools_index_show'),
    url(r'^$',                                                  'index',            name='schools_index'),
)