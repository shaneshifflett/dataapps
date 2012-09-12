"""
Stats for all districts: utils.district_query()
Stats for sincle district: utils.district_query(id)

Stats for all counties: utils.all_counties()
Stats for one county: utils.county_query(('alameda',))

Stats for all cities: utils.city_query()
Stats for one city: utils.city_query(1)

Stats for all schools: utils.school_query()
Stats for one school: utils.school_query(1)

Stats for random county: utils.random_county_query()
Stats for random city: utils.random_city_query()
Stats for random district: utils.random_district_query()
Stats for random school: utils.random_school_query()

To get a random stat of any kind: utils.random_all()
"""

import random

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import connection
from django.template.loader import render_to_string

from schools.models import SchoolDistrict, School
from locations.models import County, City
from settings import LOCAL_COUNTY_SLUGS

    

quot = lambda e: "'%s'" %e
county_template_name = 'immunizations/county_stats_sentance.html'
district_template_name = 'immunizations/district_stats_sentance.html'
city_template_name = 'immunizations/city_stats_sentance.html'
school_template_name = 'immunizations/school_stats_sentance.html'

def random_all():
    funcs = [random_county_query, random_city_query, random_district_query, random_school_query]
    return random.choice(funcs)()
    
def random_county_query():
    #get random county, call county_query
    return county_query((random.choice(LOCAL_COUNTY_SLUGS),))

def random_city_query():
    #get random city, call city_query
    #build list of city ids, store in cache
    #counties = County.objects.filter(slug__in=LOCAL_COUNTY_SLUGS)
    city_ids = cache.get('immunization_city_ids')
    if not city_ids:
        city_ids = [city.id for city in City.objects.filter(county__slug__in=LOCAL_COUNTY_SLUGS)]
        cache.set('immunization_city_ids', city_ids, 10000)
    return city_query(random.choice(city_ids))

def random_district_query():
    district_ids = cache.get('immunization_district_ids')
    if not district_ids:
        district_ids = [district.id for district in SchoolDistrict.objects.all()]
        cache.set('immunization_district_ids', district_ids, 10000)
    return district_query(random.choice(district_ids))

def random_school_query():
    school_ids = cache.get('immunization_school_ids')
    if not school_ids:
        school_ids = [school.id for school in School.objects.filter(county__slug__in=LOCAL_COUNTY_SLUGS)]
        cache.set('immunization_school_ids', school_ids, 10000)
    
    try:
        return school_query(random.choice(school_ids))
    except:
        return school_query(random.choice(school_ids))

def all_counties():
    return county_query(LOCAL_COUNTY_SLUGS)

def county_query(counties=None):
    if len(counties) == 1:
        query = """
            SELECT
            co.id id,
            SUM(i.enrollment) total_enrolled,
            SUM(i.pbe_number) total_pbe,
            FORMAT(((SUM(i.pbe_number) / SUM(i.enrollment)) * 100), 2) percent
            FROM
            immunizations_schoolimmunization i
            JOIN schools_school s ON i.school_id = s.id
            JOIN locations_county co ON s.county_id = co.id
            WHERE
            co.slug IN(%s)
            AND
            i.year = 2010
            GROUP BY co.id
        """ %",".join(map(quot, counties))
        r = County.objects.raw(query)[0]
        descriptor = "%s County" %r.name.title()
        percent = r.percent
        url = reverse('immunizations_county', kwargs={'slug': r.slug})
        return render_to_string(county_template_name, {'descriptor': descriptor, 'percent': percent, 'url': url})
    else:
        cursor = connection.cursor()
        query = """
            SELECT
            SUM(i.enrollment) total_enrolled,
            SUM(i.pbe_number) total_pbe
            FROM
            immunizations_schoolimmunization i
            JOIN schools_school s ON i.school_id = s.id
            JOIN locations_county co ON s.county_id = co.id
            WHERE
            co.slug IN(%s)
            AND
            i.year = 2010
        """ %",".join(map(quot, counties))
        cursor.execute(query)
        r = format_return(cursor.fetchall()[0])
        descriptor = "Bay Area Counties"
        percent = r['percent']
        url = reverse('immunizations_counties')
        return render_to_string(county_template_name, {'descriptor': descriptor, 'percent': percent, 'url': url})

def district_query(district_id=None):
    """ pass in slugs """
    if district_id:
        query = """
            SELECT
            d.id id,
            SUM(i.enrollment) total_enrolled,
            SUM(i.pbe_number) total_pbe,
            FORMAT(((SUM(i.pbe_number) / SUM(i.enrollment)) * 100), 2) percent
            FROM
            immunizations_schoolimmunization i
            JOIN schools_school s ON i.school_id = s.id
            JOIN schools_schooldistrict d ON s.district_id = d.id
            WHERE
            d.id = %s
            AND
            i.year = 2010
            GROUP BY d.id
        """ %district_id
        r = SchoolDistrict.objects.raw(query)[0]
        descriptor = "%s District" %r.name.title()
        percent = r.percent
        url = reverse('immunizations_district', kwargs={'slug': r.slug})
        return render_to_string(district_template_name, {'descriptor': descriptor, 'percent': percent, 'url': url})
    else:
        cursor = connection.cursor()
        query = """
            SELECT
            SUM(i.enrollment) total_enrolled,
            SUM(i.pbe_number) total_pbe,
            FORMAT(((SUM(i.pbe_number) / SUM(i.enrollment)) * 100), 2) percent
            FROM
            immunizations_schoolimmunization i
            JOIN schools_school s ON i.school_id = s.id
            JOIN schools_schooldistrict d ON s.district_id = d.id
            WHERE
            i.year = 2010
        """
        cursor.execute(query)
        r = format_return(cursor.fetchall()[0])
        descriptor = "Bay Area School Districts"
        percent = r['percent']
        url = reverse('immunizations_districts')
        return render_to_string(district_template_name, {'all': True, 'descriptor': descriptor, 'percent': percent, 'url': url})
    

def city_query(city_id=None):
    if city_id:
        query = """
            SELECT
            c.id id,
            SUM(i.enrollment) total_enrolled,
            SUM(i.pbe_number) total_pbe,
            FORMAT(((SUM(i.pbe_number) / SUM(i.enrollment)) * 100), 2) percent
            FROM
            immunizations_schoolimmunization i
            JOIN schools_school s ON i.school_id = s.id
            JOIN locations_city c ON s.city_id = c.id
            WHERE
            c.id = %s
            AND
            i.year = 2010
            GROUP BY c.id
        """ %city_id
        r = City.objects.raw(query)[0]
        descriptor = "%s" %r.name.title()
        percent = r.percent
        url = reverse('immunizations_city', kwargs={'slug': r.slug})
        return render_to_string(city_template_name, {'descriptor': descriptor, 'percent': percent, 'url': url})
    else:
        #rather than writing a new query i'm just copying the districts query since the results will be the same
        cursor = connection.cursor()
        query = """
            SELECT
            SUM(i.enrollment) total_enrolled,
            SUM(i.pbe_number) total_pbe,
            FORMAT(((SUM(i.pbe_number) / SUM(i.enrollment)) * 100), 2) percent
            FROM
            immunizations_schoolimmunization i
            JOIN schools_school s ON i.school_id = s.id
            JOIN schools_schooldistrict d ON s.district_id = d.id
            WHERE
            i.year = 2010
        """
        cursor.execute(query)
        r = format_return(cursor.fetchall()[0])
        descriptor = "Bay Area Cities"
        percent = r['percent']
        url = reverse('immunizations_cities')
        return render_to_string(city_template_name, {'all': True, 'descriptor': descriptor, 'percent': percent, 'url': url})

def school_query(school_id=None):
    if school_id:
        query = """
            SELECT
            s.id id,
            SUM(i.enrollment) total_enrolled,
            SUM(i.pbe_number) total_pbe,
            FORMAT(((SUM(i.pbe_number) / SUM(i.enrollment)) * 100), 2) percent
            FROM
            immunizations_schoolimmunization i
            JOIN schools_school s ON i.school_id = s.id
            WHERE
            s.id = %s
            AND
            i.year = 2010
            GROUP BY s.id
        """ %school_id
        r = School.objects.raw(query)[0]
        descriptor = "%s" %r.name.title()
        percent = r.percent
        url = reverse('immunizations_school', kwargs={'slug': r.slug,})
        return render_to_string(school_template_name, {'descriptor': descriptor, 'percent': percent, 'url': url})
    else:
        #rather than writing a new query i'm just copying the districts query since the results will be the same
        cursor = connection.cursor()
        query = """
            SELECT
            SUM(i.enrollment) total_enrolled,
            SUM(i.pbe_number) total_pbe,
            FORMAT(((SUM(i.pbe_number) / SUM(i.enrollment)) * 100), 2) percent
            FROM
            immunizations_schoolimmunization i
            JOIN schools_school s ON i.school_id = s.id
            JOIN schools_schooldistrict d ON s.district_id = d.id
            WHERE
            i.year = 2010
        """
        cursor.execute(query)
        r = format_return(cursor.fetchall()[0])
        descriptor = "Bay Area Schools"
        percent = r['percent']
        url = reverse('immunizations_schools')
        return render_to_string(school_template_name, {'all': True, 'descriptor': descriptor, 'percent': percent, 'url': url})

def format_return(result):
    return {'total_enrolled': result[0], 'total_pbe': result[1], 'percent': "%s" %round((float(float(result[1]) / float(result[0])) * 100), 2)}
    
