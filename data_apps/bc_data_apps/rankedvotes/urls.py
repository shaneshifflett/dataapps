from django.conf.urls import *

urlpatterns = patterns('data_apps.bc_data_apps.rankedvotes.views',
    url('^voice/$',   'voice',    name='rankedvotes_voice'),
    url('^text/$',   'text_vote',    name='rankedvotes_text_vote'),
    url('^(?P<rbid>.*?)/thanks/$', 'thanks', name='rankedvotes_thanks'),
    url('^(?P<slug>.*?)/$', 'new_ballot', name='rankedvotes_new_ballot'),
)
