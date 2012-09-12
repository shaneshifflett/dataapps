from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.decorators.cache import never_cache

from data_apps.lib.google import ftclient


from data_apps.bc_data_apps.bike_accidents.models import *
from data_apps.bc_data_apps.bike_accidents.tables import BikeAccidentTable

from data_apps.bc_apps.locations.models import City
import logging

from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.encoding import force_unicode

class LazyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj

COUNTIES = { 
    'Alameda': '5',
    'Contra Costa':'1',
    'Marin':'3',
    'Napa':'7',
    'San Francisco':'87',
    'San Mateo':'12',
    'Santa Clara':'8',
    'Solano':'16',
    'Sonoma':'25'
}

TOTAL_ACCIDENTS = 14113
GENERIC_ERROR = "Sorry, we encountered an exception processing your query. \
    We're investigating the issue but feel free to email atinio@baycitizen.org"
FT_TABLES = {
    "main":"884639",
    "counties":"820560",
    "hotspots":"868956",
    "user":""
}


def get_filters(d):
    """
    d = filters... since we are running these filters as EITHER a GET OR A POSt and 
     filters are set by a FORM or via URL PARAMETERS we have to be sexi flexi 
     with parsing.  Before we hit this method, the filters should be put in a 
     dictionary so THIS function doesn't have to worry about so many keys!
    *SIGH* if anyone has an suggestions on how to handle all these different query
    formats plz lemme know
    This function formats a query string for FUSION TABLES
    AND builds the arguments to run against DJANGO TABLES in the raw view
    AND builds a query string to append to the URL after an AJAX request so 
     folks can share the view with their settings
    """
    kwargs = {}
    filter_list = []
    url_list = []
    returns = {}
    json_response = {}
    try:
        #unpack
        date_from = d['date_from']
        date_to = d['date_to']
        accident_type = d['accident_type']
        at_fault = d['at_fault']
        violation = d['violation']
        lighting = d['lighting']
        county = d['county']
        road_condition = d['road_condition']
        pstreet = d['street1'] if 'street1' in d else None
        cstreet = d['street2'] if 'street2' in d else None
        if pstreet and cstreet:
            kwargs['primary_street__name'] = pstreet
            kwargs['cross_street__name'] = cstreet
        if date_from:
            day = date_from.day if date_from.day >= 10 else "0"+str(date_from.day)
            month = date_from.month if date_from.month >= 10 else "0"+str(date_from.month)
            filter_list.append('SimpleDate>=%s' % '%s%s%s' % (date_from.year,month,day))
            kwargs['happened_at__gte'] = date_from
            url_list.append('date_from=%s%s%s' % (date_from.year,month,day))
        if date_to:
            day = date_to.day if date_to.day >= 10 else "0"+str(date_to.day)
            month = date_to.month if date_to.month >= 10 else "0"+str(date_to.month)
            filter_list.append('SimpleDate<=%s' % '%s%s%s' % (date_to.year,month,day))
            kwargs['happened_at__lte'] = date_to
            url_list.append('date_to=%s%s%s' % (date_to.year,month,day))
        if accident_type == 'hitandrun':
            kwargs['hit_and_run'] = True
            filter_list.append("HR='YES'")
            url_list.append('accident_type=hitandrun')
        if accident_type == 'fatal':
            filter_list.append("Fatal>0")
            kwargs['fatalities'] = True
            json_response['fatal'] = 'YES'
            url_list.append('accident_type=fatal')
        if at_fault and at_fault != 'allfaults':
            kwargs['vehicle_one__name'] = at_fault
            filter_list.append("P1='%s'" % at_fault) 
            url_list.append('at_fault=%s' % at_fault)
        if violation and violation != 'allcitations':
            o = ViolationCode.objects.get(id=violation)
            filter_list.append("ViolationCategory='%s'" % o.code) 
            kwargs['violation_code__id'] = violation
            url_list.append('violation=%s' % violation)
        if lighting and lighting != 'anylighting':
            kwargs['lighting'] = lighting
            o = LightingCondition.objects.get(id=lighting)
            filter_list.append("LightingCondition='%s'" % o.name)
            url_list.append('lighting=%s' % lighting)
        if county and county != 'allcounties':
            o = Place.objects.get(id=county)
            filter_list.append("County='%s'" % o.name)
            json_response['county_name'] = o.name
            json_response['county_id'] = county
            json_response['county_tbl'] = FT_TABLES['counties']
            kwargs['county'] = county
            url_list.append('county=%s' % county)
        if road_condition and road_condition != 'allconditions':
            kwargs['road_surface'] = road_condition
            o = RoadSurface.objects.get(id=road_condition)
            filter_list.append("RoadSurface='%s'" % o.name)
            url_list.append('road_condition=%s' % road_condition)
        returns['url_list'] = url_list
        returns['json_response'] = json_response
        returns['filter_list'] = filter_list
        returns['kwargs'] = kwargs
    except Exception as e:
        logging.error("get_filters:e=%s" % e)
    return returns

def build_query_dict(form):
    """
    unpack a form set a dictionary
    Seems silly perhaps but it's easier to be consistent with a dict than
    worry about unpacking values from an AJAX POST, a GET query STR or a std POST
    """
    d = {}
    if form.is_valid():
        try:
            road_condition = form.cleaned_data.get('road_condition', None)
            county = form.cleaned_data.get('county', None)
            lighting = form.cleaned_data.get('lighting', None)
            violation = form.cleaned_data.get('violation', None)
            at_fault = form.cleaned_data.get('at_fault', None)
            accident_type = form.cleaned_data.get('accident_type', None)
            date_to = form.cleaned_data.get('date_to', None)
            date_from = form.cleaned_data.get('date_from', None)
            d['date_from'] = date_from
            d['date_to'] = date_to
            d['accident_type'] = accident_type
            d['at_fault'] = at_fault
            d['violation'] = violation
            d['lighting'] = lighting
            d['county'] = county
            d['road_condition'] = road_condition
        except Exception as e:
            logging.error('build_query_dict:e=%s' % e)
    else:
        return None
    return d
    
def get_default_filters():
    """
    set up a dictionary of keys we use throughout this app with the default
    values set to None so we don't bomb out somewhere when we try to access data
    """
    d = {}
    d['date_from'] = datetime(2005, 1, 1)
    d['date_to'] = datetime(2009, 12, 31)
    d['accident_type'] = None
    d['at_fault'] = None
    d['violation'] = None
    d['lighting'] = None
    d['county'] = None
    d['road_condition'] = None
    d['street1'] = None
    d['street2'] = None
    return d

def get_counts_ft(query):
    """
    get the total row counts from FT for a given query
    """
    ft_client = ftclient.NoLoginFTClient()
    results = ft_client.query(query)
    res_list = results.split('\n')
    if len(res_list) > 2:
        return int(res_list[1])
    else:
        return None 

@never_cache
def get_results(request, template_name='bike_accidents/bike_accidents_get_results.html'):
    """
    visualize results, get parameters from either a get requrest or an AJAX post
    """
    filter_list = []
    json_response = {}
    url_list = []
    from data_apps.bc_data_apps.bike_accidents.forms import RawDataForm
    if request.method == 'POST':
        try:
            context = {}
            ft_client = ftclient.NoLoginFTClient()
            count_query = "SELECT COUNT() FROM %s" % FT_TABLES['main']
            map_query = "SELECT FullAddress FROM %s" % FT_TABLES['main']
            form = RawDataForm(request.POST) 
            d = build_query_dict(form)
            m_results = get_filters(d)
            filter_list = m_results['filter_list']
            json_response = m_results['json_response']
            url_list = m_results['url_list']
            if filter_list:
                filter_query = build_map_query(filter_list)
                count_query = count_query + filter_query
                map_query = map_query + filter_query
                json_response['map_query'] = map_query
            json_response['query_str'] = '?' + '&'.join(url_list)
            accidents_count = get_counts_ft(count_query)
            if accidents_count:
                context['accidents_count'] = accidents_count 
                context['accidents_percent'] = (float(accidents_count) / TOTAL_ACCIDENTS) * 100
        except Exception as e:
            logging.error("bike_accidents.views.get_results: exception=%s" % e)
        json_response['results'] = render_to_string(template_name, context, context_instance=RequestContext(request))
        return HttpResponse(simplejson.dumps(json_response, cls=LazyEncoder)) 
    else:
        return HttpResponseBadRequest('bad')

def build_map_query(filter_list):
    return " WHERE " + ' AND '.join(filter_list)

def intersections(request, template_name='bike_accidents/bike_accidents_intersections.html'):
    context = {}
    context['visualization_current'] = True 
    #add_related_content_list(context) 
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def neighborhoods(request, template_name='bike_accidents/bike_accidents_neighborhoods.html'):
    context = {}
    context['visualization_current'] = True 
    #add_related_content_list(context) 
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def key_val_get_dict(request):
    """
    iterate through the request GET dictionary to get a dict of k,v
    so I can use them later for initial form values or generating filters
    """
    vals = get_default_filters()
    if len(request.GET.keys()) > 0:
        for key in request.GET.keys():
            vals[key] = request.GET.get(key)
            if key == 'date_to' or key == 'date_from':
                vals[key] = datetime.strptime(request.GET.get(key), '%Y%m%d').date()
        return vals
    else:
        return None

def index(request, template_name='bike_accidents/bike_accidents_index.html'):
    context = {}
    accidents_count = None
    from data_apps.bc_data_apps.bike_accidents.forms import RawDataForm
    form = RawDataForm()
    try:
        vals = key_val_get_dict(request)
        #no vals, no GET request, no initial settings!
        if vals != None:
            
            form = RawDataForm(initial=vals)
            m_results = get_filters(vals)
            if 'county' in request.GET.keys():
                context['default_county'] = m_results['json_response']['county_name']
                context['default_county_tbl'] = m_results['json_response']['county_tbl']
            count_query = "SELECT COUNT() FROM %s" % FT_TABLES['main']
            map_query = "SELECT FullAddress FROM %s" % FT_TABLES['main']
            #get the statements to modify the query
            filter_query = build_map_query(m_results['filter_list'])
            #append those filters to count and map query so we have a count that
            #represents our map
            count_query = count_query + filter_query
            map_query = map_query + filter_query
            #set the query to run on the map
            context['init_query'] = map_query
            accidents_count = get_counts_ft(count_query)
            url_list = m_results['url_list']
            context['query_str'] = '?' + '&'.join(url_list)
    except Exception as e:
        context['error'] = GENERIC_ERROR
        logging.error("index:exception=%s" % e)
    if accidents_count == None:
        accidents_count = TOTAL_ACCIDENTS
    context['accidents_count'] = accidents_count 
    context['accidents_percent'] = (float(accidents_count) / TOTAL_ACCIDENTS) * 100
    context['visualization_current'] = True 
    context['main_ft'] = FT_TABLES['main']
    context['form'] = form
    context['hotspots'] = FT_TABLES['hotspots']
    context['user_layeres'] = FT_TABLES['user']
    #add_related_content_list(context)
    response = render_to_response(template_name, context, context_instance=RequestContext(request))
    max_age = 60*60*24*30 # 30 days
    expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    cookie_value = request.COOKIES.get('ba_info_showhide', None)
    if cookie_value:
        response.set_cookie(key='ba_info_showhide', value=cookie_value, max_age=max_age, expires=expires)
    else:
        response.set_cookie(key='ba_info_showhide', value='shown', max_age=max_age, expires=expires)
    return response 


@never_cache    
def raw(request, template_name='bike_accidents/bike_accidents_raw.html'):
    context = {}
    context['raw_current'] = True 
    #add_related_content_list(context)
    from data_apps.bc_data_apps.bike_accidents.forms import RawDataForm
    form = RawDataForm()
    query_str = ''
    try:
        if request.method == 'POST':
            form = RawDataForm(request.POST)
            d = build_query_dict(form)
            m_results = get_filters(d)
            kwargs = m_results['kwargs']
            url_list = m_results['url_list']
            get_list = request.GET.copy()
            for u in url_list:
                kv = u.split('=')
                get_list[kv[0]] =  kv[1]
            query_str = '?' + '&'.join(url_list)
            request.GET = get_list
            if kwargs != None:
                query = BikeAccident.objects.filter(**kwargs)
            else:
                query = BikeAccident.objects.all()
        else:
            kwargs = None
            vals = key_val_get_dict(request)
            form = RawDataForm(vals)
            m_results = get_filters(vals)
            kwargs = m_results['kwargs']
            url_list = m_results['url_list']
            query_str = '?' + '&'.join(url_list)
            if kwargs != None:
                query = BikeAccident.objects.filter(**kwargs)
            else:
                query = BikeAccident.objects.all()
    except Exception as e:
        query = BikeAccident.objects.all()
        context['error'] = GENERIC_ERROR
        logging.error("raw:exception=%s" % e)
    table = BikeAccidentTable(query, order_by=request.GET.get('sort', '-date'))
    page = request.GET.get('page')
    if page == None or page == '':
        page = 1
    table.paginate(Paginator, 25, page=page, orphans=10) 
    accidents_total = BikeAccident.objects.count()
    accidents_count = query.count()
    context['accidents_count'] = accidents_count
    context['accidents_percent'] = (float(accidents_count) / accidents_total) * 100
    context['table'] = table 
    context['form'] = form
    context['query_str'] = query_str
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@never_cache    
def report(request, template_name='bike_accidents/bike_accidents_report.html'):
    context = {}
    context['report_current'] = True 
    #wiz = SubmittedAccidentsWizard([SubmittedBikeAccidentFormOne, SubmittedBikeAccidentFormTwo,\
    #    SubmittedBikeAccidentFormThree])
    wiz = SubmittedAccidentsWizard([SubmittedBikeAccidentFormOne])
    #add_related_content_list(context) 
    context['recent_accidents'] = SubmittedBikeAccident.objects.order_by('-happened_at')[:5]
    return wiz(request=request, context=RequestContext(request), extra_context=context)

@never_cache    
def thanks(request, template_name='bike_accidents/bike_accidents_thanks.html'):
    context = {}
    #add_related_content_list(context) 
    context['recent_accidents'] = SubmittedBikeAccident.objects.order_by('-happened_at')[:5]
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def sum_accidents(kwargs):
    """
    sums the accident counts 
    kwargs = options to filter our BikeAccident objects by
    accident_counts = array of total accidents for the filter
    """
    accident_counts = '['
    selected_county = None
    if kwargs.has_key('county'):
        selected_county = kwargs['county']
    counties = sorted(COUNTIES.keys())
    for county in counties:
        kwargs['county'] = COUNTIES[county]
        objs = BikeAccident.objects.filter(**kwargs)
        if selected_county == COUNTIES[county]:
            accident_counts = accident_counts + ('{y:%s, color:"#000000"},'%objs.count())
        else:
            accident_counts = accident_counts + ('%s,'%objs.count())
    accident_counts = accident_counts[0:(len(accident_counts)-1)] + ']'
    return accident_counts

def charts(request, template_name='bike_accidents/bike_accidents_charts.html'):
    context = {}
    context['charts_current'] = True 
    #add_related_content_list(context)

    from data_apps.bc_data_apps.bike_accidents.forms import RawDataForm
    form = RawDataForm()
    kwargs = {}
    try:
        if request.method == 'POST':
            form = RawDataForm(request.POST)
            d = build_query_dict(form)
            m_results = get_filters(d)
            kwargs = m_results['kwargs']
            url_list = m_results['url_list']
            context['counts'] = sum_accidents(kwargs)
            context['query_str'] = '?' + '&'.join(url_list)
        else:
            vals = key_val_get_dict(request)
            if vals != None:
                form = RawDataForm(vals)
                m_results = get_filters(vals)
                kwargs = m_results['kwargs']
                url_list = m_results['url_list']
                context['counts'] = sum_accidents(kwargs)
                context['query_str'] = '?' + '&'.join(url_list)
            else:
                context['counts'] = sum_accidents({})
    except Exception as e:
        query = BikeAccident.objects.all()
        context['error'] = GENERIC_ERROR
        logging.error("charts:exception=%s" % e)
    context['form'] = form
    context['counties'] = sorted(COUNTIES.keys())
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def analysis(request, template_name='bike_accidents/bike_accidents_analysis.html'):
    context = {}
    context['analysis_current'] = True 
    #add_related_content_list(context) 
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def methodology(request, template_name='bike_accidents/bike_accidents_methodology.html'):
    context = {}
    context['methodology_current'] = True 
    #add_related_content_list(context) 
    return render_to_response(template_name, context, context_instance=RequestContext(request))

