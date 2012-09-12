from django.conf.urls.defaults import *

urlpatterns = patterns('data_apps.bc_data_apps.rankedchoice.views',
    url('^rcv-alternate-history/$',                    'race', 
        {'slug': 'oakland-mayoral'},  name='rankedchoice_alternate_history'),
    url('^sf-mayors-race/$',                    'race', 
        {'slug': 'san-francisco-mayoral-race'},  name='rankedchoice_sf_mayor'),
    url('^sf-da-race/$',                    'race', 
        {'slug': 'san-francisco-district-attorney-race'},  name='rankedchoice_sf_da'),
    url('^sf-mayors-race/$',                    'race', 
        {'slug': 'san-francisco-sheriffs-race'},  name='rankedchoice_sf_sheriff'),
    url('^(?P<slug>.*?)/demo/$',                    'race', 
        {'template_name': 'rankedchoice/rankedchoice_race_demo.html'},  name='rankedchoice_race_demo'),
    url('^(?P<slug>.*?)/(?P<round_num>\d+)/$',      'step', name='rankedchoice_race_step'),
    url('^(?P<slug>.*?)/(?P<round_num>\d+)/text/$', 'text', name='rankedchoice_race_step_text'),
    url('^(?P<slug>.*?)/$',                         'race', name='rankedchoice_race_index'),
    url('^$',   'index',    name='rankedchoice_index'),
)
