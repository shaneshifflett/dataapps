from __future__ import division
import logging
import operator

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.http import Http404
from generics.utils import paginate_list
from immunizations import utils
from immunizations.models import SchoolImmunization, Pertussis, IzCountyAggregate, IzCityAggregate, IzSchoolAggregate, IzDistrictAggregate, ImmunizationRaw
from immunizations.queries import *
from locations.models import City, County
from schools.models import School, SchoolDistrict
from schools.queries import school_county_cities_query

def index(request):
    return counties(request)

# Apply keyword searches.
def construct_search(field_name):
    if field_name.startswith('^'):
        return "%s__istartswith" % field_name[1:]
    elif field_name.startswith('='):
        return "%s__iexact" % field_name[1:]
    elif field_name.startswith('@'):
        return "%s__search" % field_name[1:]
    else:
        return "%s__icontains" % field_name
    
def search(request, show=None, template_name="immunizations/immunizations_search.html"):
    context = {}
    context['from_page'] = 'search'
    context['initial_stat'] = utils.random_county_query()
    
    supported = ('county', 'city', 'district', 'school', 'type', 'percent_up_to_date', 'percent_conditional', 'percent_pbe', 'enrollment',)
    order = request.GET.get('order', 'county')
    o = order.replace('-', '')
    if o not in supported:
        order = 'county'
    context['order'] = order
    order = order.replace('county', 'school__county__name')
    order = order.replace('city', 'school__city__name')
    order = order.replace('district', 'district__name')
    order = order.replace('job', 'job__name')
    
    search_fields = ['school__county__name', 'school__city__name', 'district__name', 'school__name']
    q = request.GET.get('q', '')
    if q:
        for bit in q.split():
            or_queries = [models.Q(**{construct_search(str(field_name)): bit}) for field_name in search_fields]
            qs = IzSchoolAggregate.objects.filter(reduce(operator.or_, or_queries))
        rows = qs.order_by(order).distinct()
        pages, current_page = paginate_list(request, rows, limit=20)
    
        context['query'] = q
        context['pages'] = pages
        context['current_page'] = current_page
        context['rows'] = current_page.object_list
    else:
        return HttpResponseRedirect(reverse('immunizations_index'))
    
    context['page_title'] = 'Immunization Stats search results for %s' %q
    local_counties = County.local_objects.all()
    for county in local_counties:
        county.school_cities = City.objects.raw(school_county_cities_query, (county.id,))
    context['local_counties'] = local_counties    
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@never_cache
def stats_refresh(request, from_page=None):
    if from_page == 'base':
        return HttpResponse(utils.random_all())
    elif from_page == 'counties':
        return HttpResponse(utils.random_county_query())
    elif from_page == 'county':
        return HttpResponse(utils.random_all())
    elif from_page == 'cities':
        return HttpResponse(utils.random_city_query())
    elif from_page == 'city':
        return HttpResponse(utils.random_all())
    elif from_page == 'districts':
        return HttpResponse(utils.random_district_query())
    elif from_page == 'district':
        return HttpResponse(utils.random_all())
    elif from_page == 'schools':
        return HttpResponse(utils.random_school_query())
    elif from_page == 'school':
        return HttpResponse(utils.random_all())
    elif from_page == 'search':
        return HttpResponse(utils.random_all())
    else:
        raise Http404
    
def city(request, slug=None, year=2010, template_name = "immunizations/immunizations_city.html"):
    context = {}
    context['geo_type'] = 'city'
    context['city'] = city = get_object_or_404(City, slug=slug)

    supported = ('school', 'district', 'type', 'percent_up_to_date', 'percent_conditional', 'percent_pbe', 'enrollment',)
    order = request.GET.get('order', 'school')
    o = order.replace('-', '')
    if o not in supported:
        order = 'school'
    context['order'] = order
    order = order.replace('school', 'school__name')
    order = order.replace('district', 'district__name')
    
    county_data = IzCountyAggregate.objects.filter(county=city.county)
    if county_data:
        context['county_data'] = county_data[0]
    else:
        raise Http404

    city_data = IzCityAggregate.objects.filter(city=city)
    if city_data:
        context['city_data'] = city_data[0]
    else:
        raise Http404
    
    rows = IzSchoolAggregate.objects.select_related('school', 'district').filter(city=city).order_by(order)
    pages, current_page = paginate_list(request, rows, limit=20)
    
    context['pages'] = pages
    context['current_page'] = current_page
    context['rows'] = current_page.object_list
    
    
    context['page_title'] = 'Immunization Stats for City of %s' % city.name.title()
    local_counties = County.local_objects.all()
    for county in local_counties:
        county.school_cities = City.objects.raw(school_county_cities_query, (county.id,))
    context['local_counties'] = local_counties    

    context['numbers_geo_title'] = city.name
    
    high_iz_schools = SchoolImmunization.objects.filter(year=year, school__city=city
                                                        ).order_by('-up_to_date_percent')[:3]
    low_iz_schools = SchoolImmunization.objects.filter(year=year, school__city=city
                                                       ).order_by('up_to_date_percent')[:3]
    context['iz_schools'] = zip(high_iz_schools, low_iz_schools)

    high_pbe_schools  = SchoolImmunization.objects.filter(year=year, school__city=city).order_by('-pbe_percent')[:3]
    low_pbe_schools   = SchoolImmunization.objects.filter(year=year, school__city=city).order_by('pbe_percent')[:3]
    context['pbe_schools'] = zip(high_pbe_schools, low_pbe_schools)

    total_enrollment_number = SchoolImmunization.objects.filter(year=year, school__city=city
                                                                ).aggregate(Sum('enrollment'))['enrollment__sum']
    context['total_enrollment_number'] =  total_enrollment_number

    context['total_public_schools'] = total_public_schools = SchoolImmunization.objects.filter(year=year, 
                                                                                       school__city=city, 
                                                                                       school__type='PU').count()
    context['total_private_schools'] = total_private_schools = SchoolImmunization.objects.filter(year=year, 
                                                                                         school__city=city, 
                                                                                         school__type='PR').count()
    total_public = SchoolImmunization.objects.filter(year=year, school__type='PU', school__city=city
                                                                   ).aggregate(Sum('enrollment')
                                                                               )['enrollment__sum']
    total_private = SchoolImmunization.objects.filter(year=year, school__type='PR', school__city=city
                                                                   ).aggregate(Sum('enrollment')
                                                                               )['enrollment__sum']

    context['total_public_number'] = total_public
    context['total_private_number'] = total_private
    context['total_public_percent'] = 100 * (total_public/total_enrollment_number) if total_public else 0
    
    context['total_private_percent'] = 100 * (total_private/total_enrollment_number) if total_private else 0
    
    if total_public:

        total_public_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PU', school__city=city
                                                                    ).aggregate(Sum('pbe_number')
                                                                                )['pbe_number__sum']
        context['total_public_pbe_number'] = total_public_pbe_number

        context['total_public_pbe_percent'] = 100 * (total_public_pbe_number / total_public)

        total_public_iz_number = SchoolImmunization.objects.filter(year=year, school__type='PU', school__city=city
                                                                   ).aggregate(Sum('up_to_date_number')
                                                                               )['up_to_date_number__sum']
        context['total_public_iz_percent'] = 100 * (total_public_iz_number / total_public)

    if total_private:
        total_private_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PR', school__city=city
                                                                     ).aggregate(Sum('pbe_number')
                                                                                 )['pbe_number__sum']
        context['total_private_pbe_number'] = total_private_pbe_number
        context['total_private_pbe_percent'] = 100 * (total_private_pbe_number / total_private)
        
        total_private_iz_number = SchoolImmunization.objects.filter(year=year, school__type='PR', school__city=city
                                                                    ).aggregate(Sum('up_to_date_number')
                                                                                )['up_to_date_number__sum']
        context['total_private_iz_percent'] = 100 * (total_private_iz_number / total_private)

    total_pbe_number = SchoolImmunization.objects.filter(year=year, school__city=city
                                                         ).aggregate(Sum('pbe_number'))['pbe_number__sum']
    context['total_pbe_number'] = total_pbe_number
    context['total_pbe_percent'] = 100 * (total_pbe_number / total_enrollment_number)

    total_iz_number = SchoolImmunization.objects.filter(year=year, school__city=city
                                                        ).aggregate(Sum('up_to_date_number')
                                                                    )['up_to_date_number__sum']
    context['total_iz_number'] = total_iz_number
    context['total_iz_percent']  = 100 * (total_iz_number / total_enrollment_number)
    
    #Total number of conditional kindergartners across counties, and total rate of same.
    total_conditional_number = SchoolImmunization.objects.filter(year=year, school__city=city).aggregate(Sum('conditional_number'))['conditional_number__sum']
    context['total_conditional_percent'] = 100 * (total_conditional_number / total_enrollment_number)
    
    #Total number/rate of conditionals in public schools.
    total_public_conditional_number = SchoolImmunization.objects.filter(year=year, school__city=city, school__type='PU'
                                                                ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_public_conditional_percent'] = 100 * (total_public_conditional_number/total_public) if total_public else 0

    #Total number/rate of conditionals in private schools.
    total_private_conditional_number = SchoolImmunization.objects.filter(year=year, school__city=city, school__type='PR'
                                                                 ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_private_conditional_percent'] = 100 * (total_private_conditional_number/total_private) if total_private else 0

    order_arg = '-pbe_percent'
    show_filter = request.REQUEST.get('show', 'pbe_rate')

    if show_filter == 'iz_rate':
        order_arg = 'up_to_date_percent'
    elif show_filter == 'pbe_rate':
        order_arg = '-pbe_percent'

    context['pbe_displayed'] = True if show_filter == 'pbe_rate' else False
    context['school_list'] = SchoolImmunization.objects.filter(year=year, school__city=city).order_by(order_arg)[:20]
    
    #STATS DIV
    context['initial_stat'] = utils.city_query(city.id)
    context['from_page'] = 'city'
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def cities(request, year=2010, template_name="immunizations/immunizations_cities.html"):
    context = {}
    context['geo_type'] = 'city'
    context['numbers_geo_title'] = 'Bay Area Cities'
    supported = ('county', 'city', 'percent_up_to_date', 'percent_conditional', 'percent_pbe', 'enrollment', 'percent_public', 'percent_private', 'pertussis_number')
    order = request.GET.get('order', 'county')
    o = order.replace('-', '')
    if o not in supported:
        order = 'county'
    context['order'] = order
    order = order.replace('county', 'county__name')
    order = order.replace('city', 'city__name')
    
    rows = IzCityAggregate.objects.select_related('county', 'city').all().order_by(order)
    pages, current_page = paginate_list(request, rows, limit=20)
    
    context['pages'] = pages
    context['current_page'] = current_page
    context['rows'] = current_page.object_list
    
    context['page_title'] = 'Immunization Stats for all Bay Area Cities'
    local_counties = County.local_objects.all()
    for county in local_counties:
        county.school_cities = City.objects.raw(school_county_cities_query, (county.id,))
    context['local_counties'] = local_counties    

    high_iz_cities = City.objects.raw(high_iz_cities_query)
    low_iz_cities = City.objects.raw(low_iz_cities_query)    
    context['iz_cities'] = zip(high_iz_cities, low_iz_cities)

    high_pbe_cities = City.objects.raw(high_pbe_cities_query)
    low_pbe_cities = City.objects.raw(low_pbe_cities_query)
    context['pbe_cities'] = zip(high_pbe_cities, low_pbe_cities)


    total_enrollment_number = SchoolImmunization.objects.filter(year=year
                                                                ).aggregate(Sum('enrollment'))['enrollment__sum']
    context['total_enrollment_number'] = total_enrollment_number
    total_public_enrollment_number = SchoolImmunization.objects.filter(year=year,
                                                                       school__type='PU'
                                                                       ).aggregate(Sum('enrollment')
                                                                                   )['enrollment__sum']
    total_private_enrollment_number = SchoolImmunization.objects.filter(year=year,
                                                                       school__type='PR'
                                                                       ).aggregate(Sum('enrollment')
                                                                                   )['enrollment__sum']
    
   
    context['total_public_number'] = total_public_enrollment_number
    context['total_private_number'] = total_private_enrollment_number
    context['total_public_percent'] = 100 * (total_public_enrollment_number/total_enrollment_number)
    
    context['total_private_percent'] = 100 * (total_private_enrollment_number/total_enrollment_number)


    #Total number of enrolled kindergartners across cities.
    total_enrollment_number = SchoolImmunization.objects.filter(year=year).aggregate(Sum('enrollment')
                                                                                     )['enrollment__sum']
    context['total_enrollment_number'] = total_enrollment_number
    total_public_enrollment_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                       ).aggregate(Sum('enrollment'))['enrollment__sum']
    total_private_enrollment_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                        ).aggregate(Sum('enrollment'))['enrollment__sum']


    #Total number of conditional kindergartners across counties, and total rate of same.
    total_conditional_number = SchoolImmunization.objects.filter(year=year).aggregate(Sum('conditional_number'))['conditional_number__sum']
    context['total_conditional_percent'] = 100 * (total_conditional_number / total_enrollment_number)
    
    #Total number/rate of conditionals in public schools.
    total_public_conditional_number = SchoolImmunization.objects.filter(year=year,school__type='PU'
                                                                ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_public_conditional_percent'] = 100 * (total_public_conditional_number/total_public_enrollment_number)

    #Total number/rate of conditionals in private schools.
    total_private_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                 ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_private_conditional_percent'] = 100 * (total_private_conditional_number/total_private_enrollment_number)


    #Total number/rate of PBEs in public schools.
    total_public_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                ).aggregate(Sum('pbe_number'))['pbe_number__sum'] 
    context['total_public_pbe_number'] = total_public_pbe_number
    context['total_public_pbe_percent'] = 100 * (total_public_pbe_number/total_public_enrollment_number)

    #Total number/rate of PBEs in private schools.
    total_private_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                 ).aggregate(Sum('pbe_number'))['pbe_number__sum'] 
    context['total_private_pbe_number'] = total_private_pbe_number
    context['total_private_pbe_percent'] = 100 * (total_private_pbe_number/total_private_enrollment_number)

    #Total number/rate of immunization in public schools.
    total_public_up_to_date_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                       ).aggregate(Sum('up_to_date_number')
                                                                                   )['up_to_date_number__sum']
    total_public_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                        ).aggregate(Sum('conditional_number')
                                                                                    )['conditional_number__sum']
    context['total_public_iz_number'] = total_public_up_to_date_number + total_public_conditional_number
    context['total_public_iz_percent'] = 100 * ((total_public_up_to_date_number + total_public_conditional_number) / 
                                                total_public_enrollment_number)

    #Total number/rate of immunization in private schools.
    total_private_up_to_date_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                        ).aggregate(Sum('up_to_date_number')
                                                                                    )['up_to_date_number__sum']
    total_private_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                         ).aggregate(Sum('conditional_number')
                                                                                     )['conditional_number__sum']
    context['total_private_iz_number'] = total_private_up_to_date_number + total_private_conditional_number
    context['total_private_iz_percent'] = 100 * ((total_private_up_to_date_number + total_private_conditional_number) / 
                                                 total_private_enrollment_number)

    #Total number of up-to-date kindergartners across cities, and total rate of same.
    total_up_to_date_number = SchoolImmunization.objects.filter(year=year).aggregate(Sum('up_to_date_number')
                                                                                     )['up_to_date_number__sum']
    context['total_iz_number'] = total_up_to_date_number
    context['total_iz_percent'] = 100 * (total_up_to_date_number / total_enrollment_number)

    #Total number of PBE kindergartners across cities, and total rate of same.
    total_pbe_number = SchoolImmunization.objects.filter(year=year).aggregate(Sum('pbe_number'))['pbe_number__sum']
    context['total_pbe_number'] = total_pbe_number
    context['total_pbe_percent'] = 100 * (total_pbe_number / total_enrollment_number)

    #Total number of public schools across cities.
    context['total_public_schools'] = School.objects.filter(type='PU').count()
    #Total number of private schools across cities.
    context['total_private_schools'] = School.objects.filter(type='PR').count()

    order_arg = '-pbe_percent'
    show_filter = request.REQUEST.get('show', 'pbe_rate')

    if show_filter == 'iz_rate':
        order_arg = 'up_to_date_percent'
    elif show_filter == 'pbe_rate':
        order_arg = '-pbe_percent'

    context['pbe_displayed'] = True if show_filter == 'pbe_rate' else False
    context['school_list'] = SchoolImmunization.objects.filter(year=year).order_by(order_arg)[:20]

    #STATS DIV
    context['initial_stat'] = utils.city_query()
    context['from_page'] = 'cities'

    return render_to_response(template_name, context, context_instance=RequestContext(request))

def county(request, slug=None, year=2010, template_name="immunizations/immunizations_county.html"):
    context = {}
    context['geo_type'] = 'county'
    supported = ('city', 'percent_up_to_date', 'percent_pbe', 'enrollment', 'percent_public', 'percent_private', 'pertussis_number')
    order = request.GET.get('order', 'city')
    o = order.replace('-', '')
    if o not in supported:
        order = 'city'
    context['order'] = order
    order = order.replace('city', 'city__name')
    
    local_counties = County.local_objects.all()
    for county in local_counties:
        county.school_cities = City.objects.raw(school_county_cities_query, (county.id,))
    context['local_counties'] = local_counties
    
    context['county'] = county = County.objects.get(slug=slug)
    context['page_title'] = 'Immunization Stats for %s County' % county.name.title()

    context['numbers_geo_title'] = county.name + ' County'
   
    county_data = IzCountyAggregate.objects.filter(county=county)
    if county_data:
        context['county_data'] = county_data[0] 
    else:
        raise Http404
    
    context['rows'] = IzCityAggregate.objects.filter(city__county=county).order_by(order)
    context['counties_data'] = IzCountyAggregate.objects.all().order_by('county__name')

    high_iz_schools = SchoolImmunization.objects.filter(year=year, school__county=county
                                                        ).order_by('-up_to_date_percent')[:3]
    low_iz_schools = SchoolImmunization.objects.filter(year=year, school__county=county
                                                       ).order_by('up_to_date_percent')[:3]
    context['iz_schools'] = zip(high_iz_schools, low_iz_schools)

    high_pbe_schools = SchoolImmunization.objects.filter(year=year, school__county=county
                                                         ).order_by('-pbe_percent')[:3]
    low_pbe_schools = SchoolImmunization.objects.filter(year=year, school__county=county
                                                        ).order_by('pbe_percent')[:3]
    context['pbe_schools'] = zip(high_pbe_schools, low_pbe_schools)

    total_enrollment_number = SchoolImmunization.objects.filter(year=year, school__county=county
                                                                ).aggregate(Sum('enrollment'))['enrollment__sum']
    context['total_enrollment_number'] = total_enrollment_number
    total_public_enrollment_number = SchoolImmunization.objects.filter(year=year, school__county=county, 
                                                                       school__type='PU'
                                                                       ).aggregate(Sum('enrollment')
                                                                                   )['enrollment__sum']
    total_private_enrollment_number = SchoolImmunization.objects.filter(year=year, school__county=county, 
                                                                       school__type='PR'
                                                                       ).aggregate(Sum('enrollment')
                                                                                   )['enrollment__sum']
    
    
    context['total_public_number'] = total_public_enrollment_number
    context['total_private_number'] = total_private_enrollment_number
    context['total_public_percent'] = 100 * (total_public_enrollment_number/total_enrollment_number)
    
    context['total_private_percent'] = 100 * (total_private_enrollment_number/total_enrollment_number)

    total_public_pbe_number  = SchoolImmunization.objects.filter(year=year, school__type='PU', school__county=county
                                                                 ).aggregate(Sum('pbe_number'))['pbe_number__sum']
    context['total_public_pbe_number'] = total_public_pbe_number 
    context['total_public_pbe_percent'] = 100 * (total_public_pbe_number / total_public_enrollment_number)

    total_private_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PR', 
                                                                            school__county=county
                                                                            ).aggregate(Sum('pbe_number')
                                                                                        )['pbe_number__sum']
    context['total_private_pbe_number'] = total_private_pbe_number
    context['total_private_pbe_percent'] = 100 * (total_private_pbe_number / total_private_enrollment_number)

    total_public_iz_number = SchoolImmunization.objects.filter(year=year, school__type='PU', school__county=county
                                                               ).aggregate(Sum('up_to_date_number')
                                                                           )['up_to_date_number__sum']

    context['total_public_iz_percent'] = 100 * (total_public_iz_number / total_public_enrollment_number)

    total_private_iz_number = SchoolImmunization.objects.filter(year=year, school__type='PR', school__county=county
                                                               ).aggregate(Sum('up_to_date_number')
                                                                           )['up_to_date_number__sum']

    context['total_private_iz_percent'] = 100 * (total_private_iz_number / total_private_enrollment_number)

    total_pbe_number = SchoolImmunization.objects.filter(year=year, school__county=county
                                                         ).aggregate(Sum('pbe_number'))['pbe_number__sum']
    context['total_pbe_number']  = total_pbe_number 
    
    context['total_pbe_percent'] = 100 * (total_pbe_number / total_enrollment_number)
    
    logging.debug('Cache: county: %s' %county)
    total_iz_number = SchoolImmunization.objects.filter(year=year, school__county=county
                                                        ).aggregate(Sum('up_to_date_number')
                                                                    )['up_to_date_number__sum']
    context['total_iz_number'] = total_iz_number

    context['total_iz_percent'] = 100 * (total_iz_number / total_enrollment_number)
    logging.debug('Cache: total_iz_percent: %s' %context['total_iz_percent'])
    
    context['total_public_schools'] = School.objects.filter(type='PU', county=county).count()
    context['total_private_schools'] = School.objects.filter(type='PR', county=county).count()

    context['pertussis'] = Pertussis.objects.get(year=2011, county=county)
    
    #Total number of conditional kindergartners across counties, and total rate of same.
    total_conditional_number = SchoolImmunization.objects.filter(year=year, school__county=county).aggregate(Sum('conditional_number'))['conditional_number__sum']
    context['total_conditional_percent'] = 100 * (total_conditional_number / total_enrollment_number)
    
    #Total number/rate of conditionals in public schools.
    total_public_conditional_number = SchoolImmunization.objects.filter(year=year, school__county=county, school__type='PU'
                                                                ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_public_conditional_percent'] = 100 * (total_public_conditional_number/total_public_enrollment_number)

    #Total number/rate of conditionals in private schools.
    total_private_conditional_number = SchoolImmunization.objects.filter(year=year, school__county=county, school__type='PR'
                                                                 ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_private_conditional_percent'] = 100 * (total_private_conditional_number/total_private_enrollment_number)

    order_arg = '-pbe_percent'
    show_filter = request.REQUEST.get('show', 'pbe_rate')

    if show_filter == 'iz_rate':
        order_arg = 'up_to_date_percent'
    elif show_filter == 'pbe_rate':
        order_arg = '-pbe_percent'

    context['pbe_displayed'] = True if show_filter == 'pbe_rate' else False
    context['school_list'] = SchoolImmunization.objects.filter(year=year, school__county=county).order_by(order_arg
                                                                                                          )[:20]

    #STATS DIV
    context['initial_stat'] = utils.county_query((county.slug,))
    context['from_page'] = 'county'

    return render_to_response(template_name, context, context_instance=RequestContext(request))

def pbe_graph(request, template_name='immunizations/partials/personal_belief_graph.html'):
    context = {}
    context['counties_data'] = IzCountyAggregate.objects.all().order_by('county__name')
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def county_compare_graph(request, template_name='immunizations/partials/comparison_graph.html'):
    context = {}
    context['counties_data'] = IzCountyAggregate.objects.all().order_by('county__name')
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def counties(request, year=2010, template_name='immunizations/immunizations_index.html'):
    context = {}
    context['page_title'] = 'Immunization Stats for all Bay Area Counties'
    context['geo_type'] = 'county'
    context['numbers_geo_title'] = 'Bay Area Counties'
    
    supported = ('county', 'percent_up_to_date', 'percent_pbe', 'enrollment', 'percent_public', 'percent_private', 'pertussis_number')
    order = request.GET.get('order', 'county')
    o = order.replace('-', '')
    if o not in supported:
        order = 'county'
    context['order'] = order
    order = order.replace('county', 'county__name')
    context['rows'] = IzCountyAggregate.objects.all().order_by(order)
    context['counties_data'] = IzCountyAggregate.objects.all().order_by('county__name')
    
    local_counties = County.local_objects.all()
    for county in local_counties:
        county.school_cities = City.objects.raw(school_county_cities_query, (county.id,))
    context['local_counties'] = local_counties    

    high_iz_counties = County.objects.raw(high_iz_counties_query)
    low_iz_counties = County.objects.raw(low_iz_counties_query)
    context['iz_counties'] = zip(high_iz_counties, low_iz_counties)

    high_pbe_counties = County.objects.raw(high_pbe_counties_query)
    low_pbe_counties = County.objects.raw(low_pbe_counties_query)    
    context['pbe_counties'] = zip(high_pbe_counties, low_pbe_counties)

    high_pertussis_rates = Pertussis.objects.filter(year=2011).order_by('-rate')[:3]
    low_pertussis_rates = Pertussis.objects.filter(year=2011).order_by('rate')[:3]
    
    context['pertussis_rates'] = zip(high_pertussis_rates, low_pertussis_rates)

    #Total number of enrolled kindergartners across counties.
    total_enrollment_number = SchoolImmunization.objects.filter(year=year
                                                                ).aggregate(Sum('enrollment'))['enrollment__sum']
    context['total_enrollment_number'] = total_enrollment_number

    total_public_enrollment_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                       ).aggregate(Sum('enrollment')
                                                                                   )['enrollment__sum']
    context['total_public_percent'] = 100 * (total_public_enrollment_number/total_enrollment_number)
    total_private_enrollment_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                        ).aggregate(Sum('enrollment')
                                                                                    )['enrollment__sum']
    context['total_private_percent'] = 100 * (total_private_enrollment_number/total_enrollment_number)
    context['total_public_number'] = total_public_enrollment_number
    context['total_private_number'] = total_private_enrollment_number
    
    #Total number/rate of immunization in public schools.
    total_public_up_to_date_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                       ).aggregate(Sum('up_to_date_number')
                                                                                   )['up_to_date_number__sum']
    context['total_public_iz_percent'] = 100 * (total_public_up_to_date_number/total_public_enrollment_number)

    #Total number/rate of immunization in private schools.
    total_private_up_to_date_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                        ).aggregate(Sum('up_to_date_number')
                                                                                    )['up_to_date_number__sum']
    context['total_private_iz_percent'] = 100 * (total_private_up_to_date_number/total_private_enrollment_number)

    #Total number of up-to-date kindergartners across counties, and total rate of same.
    total_up_to_date_number = SchoolImmunization.objects.filter(year=year
                                                                ).aggregate(Sum('up_to_date_number')
                                                                            )['up_to_date_number__sum']
    context['total_iz_percent'] = 100 * (total_up_to_date_number / total_enrollment_number)

    #Total number of PBE kindergartners across counties, and total rate of same.
    total_pbe_number = SchoolImmunization.objects.filter(year=year).aggregate(Sum('pbe_number'))['pbe_number__sum']
    context['total_pbe_percent'] = 100 * (total_pbe_number / total_enrollment_number)

    #Total number/rate of PBEs in public schools.
    total_public_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                ).aggregate(Sum('pbe_number'))['pbe_number__sum'] 
    context['total_public_pbe_percent'] = 100 * (total_public_pbe_number/total_public_enrollment_number)

    #Total number/rate of PBEs in private schools.
    total_private_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                 ).aggregate(Sum('pbe_number'))['pbe_number__sum'] 
    context['total_private_pbe_percent'] = 100 * (total_private_pbe_number/total_private_enrollment_number)
    
    #Total number of conditional kindergartners across counties, and total rate of same.
    total_conditional_number = SchoolImmunization.objects.filter(year=year).aggregate(Sum('conditional_number'))['conditional_number__sum']
    context['total_conditional_percent'] = 100 * (total_conditional_number / total_enrollment_number)
    
    #Total number/rate of conditionals in public schools.
    total_public_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_public_conditional_percent'] = 100 * (total_public_conditional_number/total_public_enrollment_number)

    #Total number/rate of conditionals in private schools.
    total_private_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                 ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_private_conditional_percent'] = 100 * (total_private_conditional_number/total_private_enrollment_number)
    
    #STATS DIV
    context['initial_stat'] = utils.all_counties()
    context['from_page'] = 'counties'

    return render_to_response(template_name, context, context_instance=RequestContext(request))

def district(request, slug=None, year=2010, template_name='immunizations/immunizations_district.html'):
    context = {}
    context['district'] = district = SchoolDistrict.objects.get(slug=slug)
    context['page_title'] = 'Immunization Stats for %s District' % district.name.title()
    
    supported = ('school', 'type', 'percent_up_to_date', 'percent_conditional', 'percent_pbe', 'enrollment',)
    order = request.GET.get('order', 'school')
    o = order.replace('-', '')
    if o not in supported:
        order = 'school'
    context['order'] = order
    order = order.replace('school', 'school__name')
    
    s = School.objects.filter(district=district, county__isnull=False)[0]
    county_data = IzCountyAggregate.objects.filter(county=s.county)
    if county_data:
        context['county_data'] = county_data[0] 
    else:
        raise Http404
    
    district_data = IzDistrictAggregate.objects.filter(district=district)    
    if district_data:
        context['district_data'] = district_data[0]
    else:
        raise Http404
    
    rows = IzSchoolAggregate.objects.select_related('school').filter(school__district=district).order_by(order)
    pages, current_page = paginate_list(request, rows, limit=20)
    
    context['pages'] = pages
    context['current_page'] = current_page
    context['rows'] = current_page.object_list
    
    local_counties = County.local_objects.all()
    for county in local_counties:
        county.school_cities = City.objects.raw(school_county_cities_query, (county.id,))
    context['local_counties'] = local_counties    

    high_iz_schools  = SchoolImmunization.objects.filter(year=year, school__district=district
                                                                    ).order_by('-up_to_date_percent')[:3]
    low_iz_schools   = SchoolImmunization.objects.filter(year=year, school__district=district
                                                                    ).order_by('up_to_date_percent')[:3]
    context['iz_schools'] = zip(high_iz_schools, low_iz_schools)
    
    high_pbe_schools  = SchoolImmunization.objects.filter(year=year, school__district=district
                                                                     ).order_by('-pbe_percent')[:3]
    low_pbe_schools   = SchoolImmunization.objects.filter(year=year, school__district=district
                                                                     ).order_by('pbe_percent')[:3]
    context['pbe_schools'] = zip(high_pbe_schools, low_pbe_schools)

    context['total_enrollment_number'] = total_enrollment_number = SchoolImmunization.objects.filter(year=year,
                                                                            school__district=district
                                                                            ).aggregate(Sum('enrollment')
                                                                                        )['enrollment__sum']
    
    context['total_pbe_number']  = total_pbe_number = SchoolImmunization.objects.filter(year=year, 
                                                                                        school__district=district
                                                                                        ).aggregate(Sum('pbe_number')
                                                                                                    )['pbe_number__sum']
    context['total_pbe_percent']  = 100 * (total_pbe_number / total_enrollment_number)

    context['total_iz_number']  = total_iz_number = SchoolImmunization.objects.filter(year=year, school__district=district
                                                                    ).aggregate(Sum('up_to_date_number')
                                                                                )['up_to_date_number__sum']
    context['total_iz_percent']  = 100 * (total_iz_number / total_enrollment_number)

    context['total_public_schools'] = School.objects.filter(type='PU', district=district).count()
    
    #Total number of conditional kindergartners across counties, and total rate of same.
    total_conditional_number = SchoolImmunization.objects.filter(year=year, school__district=district).aggregate(Sum('conditional_number'))['conditional_number__sum']
    context['total_conditional_percent'] = 100 * (total_conditional_number / total_enrollment_number)
    

    order_arg = '-pbe_percent'
    show_filter = request.REQUEST.get('show', 'pbe_rate')

    if show_filter == 'iz_rate':
        order_arg = 'up_to_date_percent'
    elif show_filter == 'pbe_rate':
        order_arg = '-pbe_percent'

    context['pbe_displayed'] = True if show_filter == 'pbe_rate' else False
    context['school_list'] = SchoolImmunization.objects.filter(year=year, school__district=district
                                                               ).order_by(order_arg)[:20]
    
    #STATS DIV
    context['initial_stat'] = utils.district_query(district.id)
    context['from_page'] = 'district'
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def districts(request, year=2010, template_name='immunizations/immunizations_districts.html'):
    context = {}
    context['page_title'] = 'Immunization Stats for all Bay Area School Districts'
    context['numbers_geo_title'] = 'Bay Area School Districts'
    
    supported = ('county', 'district', 'percent_up_to_date', 'percent_conditional', 'percent_pbe', 'enrollment',)
    order = request.GET.get('order', 'county')
    o = order.replace('-', '')
    if o not in supported:
        order = 'county'
    context['order'] = order
    order = order.replace('county', 'county__name')
    
    rows = IzDistrictAggregate.objects.select_related('school').all().order_by(order)
    pages, current_page = paginate_list(request, rows, limit=20)
    
    context['pages'] = pages
    context['current_page'] = current_page
    context['rows'] = current_page.object_list
    
    local_counties = County.local_objects.all()
    for county in local_counties:
        county.school_cities = City.objects.raw(school_county_cities_query, (county.id,))
    context['local_counties'] = local_counties    
    
    high_iz_districts = SchoolDistrict.objects.raw(high_iz_districts_query)
    low_iz_districts = SchoolDistrict.objects.raw(low_iz_districts_query)    
    context['iz_districts'] = zip(high_iz_districts, low_iz_districts)

    high_pbe_districts = SchoolDistrict.objects.raw(high_pbe_districts_query)
    low_pbe_districts = SchoolDistrict.objects.raw(low_pbe_districts_query)
    context['pbe_districts'] = zip(high_pbe_districts, low_pbe_districts)



    #Total number of enrolled kindergartners across counties.
    total_enrollment_number = SchoolImmunization.objects.filter(year=year
                                                                ).aggregate(Sum('enrollment'))['enrollment__sum']
    context['total_enrollment_number'] = total_enrollment_number

    total_public_enrollment_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                       ).aggregate(Sum('enrollment')
                                                                                   )['enrollment__sum']
    context['total_public_percent'] = 100 * (total_public_enrollment_number/total_enrollment_number)
    total_private_enrollment_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                        ).aggregate(Sum('enrollment')
                                                                                    )['enrollment__sum']
    context['total_private_percent'] = 100 * (total_private_enrollment_number/total_enrollment_number)
    context['total_public_number'] = total_public_enrollment_number
    context['total_private_number'] = total_private_enrollment_number
    
    #Total number/rate of immunization in public schools.
    total_public_up_to_date_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                       ).aggregate(Sum('up_to_date_number')
                                                                                   )['up_to_date_number__sum']
    context['total_public_iz_percent'] = 100 * (total_public_up_to_date_number/total_public_enrollment_number)

    #Total number/rate of immunization in private schools.
    total_private_up_to_date_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                        ).aggregate(Sum('up_to_date_number')
                                                                                    )['up_to_date_number__sum']
    context['total_private_iz_percent'] = 100 * (total_private_up_to_date_number/total_private_enrollment_number)

    #Total number of up-to-date kindergartners across counties, and total rate of same.
    total_up_to_date_number = SchoolImmunization.objects.filter(year=year
                                                                ).aggregate(Sum('up_to_date_number')
                                                                            )['up_to_date_number__sum']
    context['total_iz_percent'] = 100 * (total_up_to_date_number / total_enrollment_number)

    #Total number of PBE kindergartners across counties, and total rate of same.
    total_pbe_number = SchoolImmunization.objects.filter(year=year).aggregate(Sum('pbe_number'))['pbe_number__sum']
    context['total_pbe_percent'] = 100 * (total_pbe_number / total_enrollment_number)

    #Total number/rate of PBEs in public schools.
    total_public_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                ).aggregate(Sum('pbe_number'))['pbe_number__sum'] 
    context['total_public_pbe_percent'] = 100 * (total_public_pbe_number/total_public_enrollment_number)

    #Total number/rate of PBEs in private schools.
    total_private_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                 ).aggregate(Sum('pbe_number'))['pbe_number__sum'] 
    context['total_private_pbe_percent'] = 100 * (total_private_pbe_number/total_private_enrollment_number)
    
    #Total number of conditional kindergartners across counties, and total rate of same.
    total_conditional_number = SchoolImmunization.objects.filter(year=year).aggregate(Sum('conditional_number'))['conditional_number__sum']
    context['total_conditional_percent'] = 100 * (total_conditional_number / total_enrollment_number)
    
    #Total number/rate of conditionals in public schools.
    total_public_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_public_conditional_percent'] = 100 * (total_public_conditional_number/total_public_enrollment_number)

    #Total number/rate of conditionals in private schools.
    total_private_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                 ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_private_conditional_percent'] = 100 * (total_private_conditional_number/total_private_enrollment_number)

    #zzzzzzzzzzzzzzzz


    order_arg = '-pbe_percent'
    show_filter = request.REQUEST.get('show', 'pbe_rate')

    if show_filter == 'iz_rate':
        order_arg = 'up_to_date_percent'
    elif show_filter == 'pbe_rate':
        order_arg = '-pbe_percent'

    context['pbe_displayed'] = True if show_filter == 'pbe_rate' else False
    context['school_list'] = SchoolImmunization.objects.filter(year=year, school__type='PU').order_by(order_arg)[:20]
    
    #STATS DIV
    context['initial_stat'] = utils.district_query()
    context['from_page'] = 'districts'

    return render_to_response(template_name, context, context_instance=RequestContext(request))

def school(request, slug=None, year=2010, template_name="immunizations/immunizations_school.html"):
    context = {}
    context['school'] = school = get_object_or_404(School, slug=slug)
    #check to see if current year data exists, if not, throw a 404
    #bc some calculations rely on current year data
    schoolimmunization = SchoolImmunization.objects.filter(school__id=school.id, year=year, school__city=school.city)
    if len(schoolimmunization) < 1:
        raise Http404
    context['page_title'] = 'Immunization Stats for %s' % school.name.title()
    local_counties = County.local_objects.all()
    for county in local_counties:
        county.school_cities = City.objects.raw(school_county_cities_query, (county.id,))
    context['local_counties'] = local_counties    

    try:
        context['iz_2009'] = SchoolImmunization.objects.get(year=year, school=school)
    except:
        context['iz_2009'] = None
    try:
        context['iz_2008'] = SchoolImmunization.objects.get(year=2008, school=school)
    except:
        context['iz_2008'] = None
    
    try:
        context['iz_2007'] = SchoolImmunization.objects.get(year=2007, school=school)
    except:
        context['iz_2007'] = None

    if school.district:
        district_enrollment_number = SchoolImmunization.objects.filter(year=year, school__district=school.district,
                                                                       ).aggregate(Sum('enrollment')
                                                                                   )['enrollment__sum']

        #Total number of up-to-date kindergartners across district
        district_up_to_date_number = SchoolImmunization.objects.filter(year=year, school__district=school.district,
                                                                       ).aggregate(Sum('up_to_date_number')
                                                                                )['up_to_date_number__sum']
        context['district_iz_percent'] = 100 * (district_up_to_date_number / district_enrollment_number)
        #Total number of PBE kindergartners across district
        district_pbe_number = SchoolImmunization.objects.filter(year=year, school__district=school.district,
                                                                ).aggregate(Sum('pbe_number'))['pbe_number__sum']
        context['district_pbe_percent'] = 100 * (district_pbe_number / district_enrollment_number)

    city_enrollment_number = SchoolImmunization.objects.filter(year=year, school__city=school.city
                                                                ).aggregate(Sum('enrollment'))['enrollment__sum']
    city_pbe_number = SchoolImmunization.objects.filter(year=year, school__city=school.city
                                                         ).aggregate(Sum('pbe_number'))['pbe_number__sum']
    context['city_pbe_percent'] = 100 * (city_pbe_number / city_enrollment_number)
    city_iz_number = SchoolImmunization.objects.filter(year=year, school__city=school.city
                                                        ).aggregate(Sum('up_to_date_number')
                                                                    )['up_to_date_number__sum']
    context['city_iz_percent']  = 100 * (city_iz_number / city_enrollment_number)

    county_enrollment_number = SchoolImmunization.objects.filter(year=year, school__county=school.county
                                                                ).aggregate(Sum('enrollment'))['enrollment__sum']
    county_pbe_number = SchoolImmunization.objects.filter(year=year, school__county=school.county
                                                         ).aggregate(Sum('pbe_number'))['pbe_number__sum']
    context['county_pbe_percent'] = 100 * (county_pbe_number / county_enrollment_number)
    county_iz_number = SchoolImmunization.objects.filter(year=year, school__county=school.county
                                                        ).aggregate(Sum('up_to_date_number')
                                                                    )['up_to_date_number__sum']
    context['county_iz_percent'] = 100 * (county_iz_number / county_enrollment_number)
    
    #STATS DIV
    context['initial_stat'] = utils.school_query(school.id)
    context['from_page'] = 'school'
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def schools(request, year=2010, template_name='immunizations/immunizations_schools.html'):
    context = {}
    context['numbers_geo_title'] = 'Bay Area Schools'
    
    supported = ('school', 'district', 'type', 'percent_up_to_date', 'percent_conditional', 'percent_pbe', 'enrollment',)
    order = request.GET.get('order', 'school')
    o = order.replace('-', '')
    if o not in supported:
        order = 'school'
    context['order'] = order
    order = order.replace('school', 'school__name')
    order = order.replace('district', 'district__name')
    
    rows = IzSchoolAggregate.objects.select_related('school', 'district').all().order_by(order)
    pages, current_page = paginate_list(request, rows, limit=20)
    
    context['pages'] = pages
    context['current_page'] = current_page
    context['rows'] = current_page.object_list
    
    context['page_title'] = 'Immunization Stats for all Bay Area Schools'
    local_counties = County.local_objects.all()
    for county in local_counties:
        county.school_cities = City.objects.raw(school_county_cities_query, (county.id,))
    context['local_counties'] = local_counties    

    high_iz_schools = School.objects.raw(high_iz_schools_query)
    low_iz_schools = School.objects.raw(low_iz_schools_query)    
    context['iz_schools'] = zip(high_iz_schools, low_iz_schools)

    high_pbe_schools = School.objects.raw(high_pbe_schools_query)
    low_pbe_schools = School.objects.raw(low_pbe_schools_query)
    context['pbe_schools'] = zip(high_pbe_schools, low_pbe_schools)


    #Total number of enrolled kindergartners across counties.
    total_enrollment_number = SchoolImmunization.objects.filter(year=year
                                                                ).aggregate(Sum('enrollment'))['enrollment__sum']
    context['total_enrollment_number'] = total_enrollment_number

    total_public_enrollment_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                       ).aggregate(Sum('enrollment')
                                                                                   )['enrollment__sum']
    context['total_public_percent'] = 100 * (total_public_enrollment_number/total_enrollment_number)
    total_private_enrollment_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                        ).aggregate(Sum('enrollment')
                                                                                    )['enrollment__sum']
    context['total_private_percent'] = 100 * (total_private_enrollment_number/total_enrollment_number)

    context['total_public_number'] = total_public_enrollment_number
    context['total_private_number'] = total_private_enrollment_number

    #Total number/rate of PBEs in public schools.
    total_public_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                ).aggregate(Sum('pbe_number'))['pbe_number__sum'] 
    context['total_public_pbe_number'] = total_public_pbe_number
    context['total_public_pbe_percent'] = 100 * (total_public_pbe_number/total_public_enrollment_number)

    #Total number/rate of PBEs in private schools.
    total_private_pbe_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                 ).aggregate(Sum('pbe_number'))['pbe_number__sum'] 
    context['total_private_pbe_number'] = total_private_pbe_number
    context['total_private_pbe_percent'] = 100 * (total_private_pbe_number/total_private_enrollment_number)

    #Total number/rate of immunization in public schools.
    total_public_up_to_date_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                       ).aggregate(Sum('up_to_date_number')
                                                                                   )['up_to_date_number__sum']
    total_public_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                        ).aggregate(Sum('conditional_number')
                                                                                    )['conditional_number__sum']
    context['total_public_iz_number'] = total_public_up_to_date_number + total_public_conditional_number
    context['total_public_iz_percent'] = 100 * ((total_public_up_to_date_number + total_public_conditional_number) / 
                                                total_public_enrollment_number)

    #Total number/rate of immunization in private schools.
    total_private_up_to_date_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                        ).aggregate(Sum('up_to_date_number')
                                                                                    )['up_to_date_number__sum']
    total_private_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                         ).aggregate(Sum('conditional_number')
                                                                                     )['conditional_number__sum']
    context['total_private_iz_number'] = total_private_up_to_date_number + total_private_conditional_number
    context['total_private_iz_percent'] = 100 * ((total_private_up_to_date_number + total_private_conditional_number) / 
                                                 total_private_enrollment_number)


    #Total number of conditional kindergartners across counties, and total rate of same.
    total_conditional_number = SchoolImmunization.objects.filter(year=year).aggregate(Sum('conditional_number'))['conditional_number__sum']
    context['total_conditional_percent'] = 100 * (total_conditional_number / total_enrollment_number)
    
    #Total number/rate of conditionals in public schools.
    total_public_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PU'
                                                                ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_public_conditional_percent'] = 100 * (total_public_conditional_number/total_public_enrollment_number)

    #Total number/rate of conditionals in private schools.
    total_private_conditional_number = SchoolImmunization.objects.filter(year=year, school__type='PR'
                                                                 ).aggregate(Sum('conditional_number'))['conditional_number__sum'] 
    context['total_private_conditional_percent'] = 100 * (total_private_conditional_number/total_private_enrollment_number)

    #Total number of up-to-date kindergartners across counties, and total rate of same.
    total_up_to_date_number = SchoolImmunization.objects.filter(year=year
                                                                ).aggregate(Sum('up_to_date_number')
                                                                            )['up_to_date_number__sum']
    context['total_up_to_date_number'] = total_up_to_date_number
    context['total_up_to_date_percent'] = 100 * (total_up_to_date_number / total_enrollment_number)
    #Total number of PBE kindergartners across counties, and total rate of same.
    total_pbe_number = SchoolImmunization.objects.filter(year=year).aggregate(Sum('pbe_number'))['pbe_number__sum']
    context['total_pbe_number'] = total_pbe_number
    context['total_pbe_percent'] = 100 * (total_pbe_number / total_enrollment_number)

    #Average immunization rate across counties.
    context['total_iz_percent'] = 100 * (((total_public_up_to_date_number + total_public_conditional_number) +
                                         (total_private_up_to_date_number + total_private_conditional_number)) / 
                                         total_enrollment_number)

    #Total number of public schools across counties.
    context['total_public_schools'] = School.objects.filter(type='PU').count()
    #Total number of private schools across counties.
    context['total_private_schools'] = School.objects.filter(type='PR').count()

    order_arg = '-pbe_percent'
    show_filter = request.REQUEST.get('show', 'pbe_rate')

    if show_filter == 'iz_rate':
        order_arg = 'up_to_date_percent'
    elif show_filter == 'pbe_rate':
        order_arg = '-pbe_percent'

    context['pbe_displayed'] = True if show_filter == 'pbe_rate' else False
    context['school_list'] = SchoolImmunization.objects.filter(year=year).order_by(order_arg)[:20]

    #STATS DIV
    context['initial_stat'] = utils.school_query()
    context['from_page'] = 'schools'
    return render_to_response(template_name, context, context_instance=RequestContext(request))
