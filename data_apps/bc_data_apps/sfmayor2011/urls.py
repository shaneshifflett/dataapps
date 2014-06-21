from django.conf.urls import *

urlpatterns = patterns('bc_data_apps.dataapps.sfmayor2011.views',
    url('^candidates/$', 'list_candidates', name='sfmayor_list_candidates'),
    url('^candidates/(?P<slug>[\w-]+)/$', 'candidate', name='sfmayor_candidate'),
    url('^candidates/(?P<slug>[\w-]+)/p/$', 'get_content_candidates', name='sfmayor_get_content_candidates'),
    url('^contributions/$', 'contributions', name='sfmayor_contributions'),
    url('^contributions/db/$', 'contributions_list', name='sfmayor_contributions_list'),
    url('^contributions/db/(?P<slug>[\w-]+)/$', 'contributions_list', name='sfmayor_candidate_contributions'),
    url('^contributions-map/$', 'contributions_map', name='sfmayor_contributions_map'),
    url('^poll-locations/$', 'poll_locations', name='sfmayor_poll_places'),
    url('^questions/$', 'ask_candidate', name='sfmayor_questions'),
    url('^faq/$', 'faq', name='sfmayor_faq'),
    url('^p/$', 'get_content', name='sfmayor_get_content'),
    url('^$', 'index', name='sfmayor_index')
)
