from django.conf.urls.defaults import *

urlpatterns = patterns('bc_data_apps.dataapps.census2010.views',
	url('^$', 'list', {'geography':'county'}, name='census2010_index'),
	url('^counties/$', 'list', {'geography':'county'}, name='census2010_county_list'),
	url('^cities/$', 'list', {'geography':'place'}, name='census2010_city_list'),
	url('^tracts/$', 'list', {'geography':'tract'}, name='census2010_tract_list'),
	url('^assemblies/$', 'legislative_list', {'geography':'legislative_lower'}, name='census2010_assembly_list'),
	url('^senate/$', 'legislative_list', {'geography':'legislative_upper'}, name='census2010_senate_list'),
	url('^congressional/$', 'legislative_list', {'geography':'congressional'}, name='census2010_congressional_list'),
	url('^cities/(?P<slug>[\w-]+)/$', 'detail', name='census2010_city_detail'),
	url('^counties/(?P<slug>[\w-]+)/$', 'detail', name='census2010_county_detail'),
	url('^senate/(?P<slug>[\w-]+)/$', 'legislative_detail', name='census2010_senate_detail'),
	url('^assemblies/(?P<slug>[\w-]+)/$', 'legislative_detail', name='census2010_assembly_detail'),
	url('^congressional/(?P<slug>[\w-]+)/$', 'legislative_detail', name='census2010_congressional_detail'),
	url('^tracts/(?P<slug>[\w-]+)/$', 'detail', name='census2010_tract_detail')
)
