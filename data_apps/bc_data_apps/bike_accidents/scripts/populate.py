import csv, os, re, urllib2
from datetime import datetime

from django.conf import settings

import BeautifulSoup
from simplegeo import Client

from bike_accidents.models import *
from generics.cleaner import CleanHtml
from locations import utils as locationutils

base_url = 'http://www.dmv.ca.gov/pubs/vctop/d11/vc%s.htm'

months = {
          'Jan.': 1,
          'Feb.': 2,
          'Mar.': 3,
          'Apr.': 4,
          'May.': 5,
          'Jun.': 6,
          'Jul.': 7,
          'Aug.': 8,
          'Sep.': 9,
          'Oct.': 10,
          'Nov.': 11,
          'Dec.': 12
}

bad_violation_codes = ('OTD', 'NS', 'UNK', 'OID')

directions = {
              'N': 'north',
              'S': 'south',
              'E': 'east',
              'W': 'west',
}

def five_year_all_counties():
    contents = csv.reader(open("%s/../files/five_year_all_counties.csv" %os.path.dirname(__file__)), dialect='excel', delimiter=',', quotechar='"')
    contents.next()
    #map csv headers to fields in class
    fm = {
        "case_number":0,
        "happened_at":14,
        "primary_street":9,
        "cross_street":10,
        "full_address":11,
        "feet_from_intersection":12,
        "vehicle_one":15,
        "vehicle_two":20,
        "fatalities":22,
        "hit_and_run":24,
        "violation_code":25,
        "violation_category":26,
        "county":27,
        "city":28,
        "lighting":29,
        "road_surface":30,
        "direction_from_intersection":13,
        "injured":23,
        "hour":7,
        "min":8,
        "year":3,
        "month":4,
        "day":5
    }

    for row in contents:
        case_number = row[fm["case_number"]]
        
        happened_at = datetime(int(row[fm['year']]), int(row[fm['month']]), int(row[fm['day']]),\
         int(row[fm['hour']]), int(row[fm['min']]), 0)
        v_category = row[fm["violation_category"]].strip()
        violation_code, created = ViolationCode.objects.get_or_create(code=v_category)
        primary_street, created = Street.objects.get_or_create(name=row[fm["primary_street"]].strip())
        cross_street, created = Street.objects.get_or_create(name=row[fm["cross_street"]].strip())
        full_address, created = FullAddress.objects.get_or_create(name=row[fm["full_address"]].strip())
        vehicle_one, created = Vehicle.objects.get_or_create(name=row[fm["vehicle_one"]].strip())
        vehicle_two, created = Vehicle.objects.get_or_create(name=row[fm["vehicle_two"]].strip())
        fatalities = row[fm["fatalities"]]
        hit_and_run = row[fm["hit_and_run"]] == 'YES'
        county, created = Place.objects.get_or_create(name=row[fm["county"]].strip())
        city, created = Place.objects.get_or_create(name=row[fm["city"]].strip())
        lighting, created = LightingCondition.objects.get_or_create(name=row[fm["lighting"]].strip())
        road_surface, created = RoadSurface.objects.get_or_create(name=row[fm["road_surface"]].strip())
        d_f_i = row[fm['direction_from_intersection']].strip()
        injured = row[fm['injured']].strip()
        feet_from_intersection = row[fm['feet_from_intersection']].strip()
        
        BikeAccident(happened_at=happened_at, case_number=case_number, \
        violation_code=violation_code, primary_street=primary_street, \
        cross_street=cross_street, full_address=full_address, \
        vehicle_one=vehicle_one, vehicle_two=vehicle_two, fatalities=fatalities,\
        hit_and_run=hit_and_run, county=county, city=city, lighting=lighting,\
        road_surface=road_surface, direction_from_intersection=d_f_i,\
        injured=injured, feet_from_intersection=feet_from_intersection).save()
        

def run():
    contents = csv.reader(open("%s/../files/bike_accidents.csv" %os.path.dirname(__file__)), dialect='excel', delimiter=',', quotechar='"')
    writer = csv.writer(open("%s/../files/bike_accidents_complete.csv" %os.path.dirname(__file__), 'wb'))

    header = contents.next()
    writer.writerow(header)
    i = 0
    j = 0
    for row in contents:
        case_number = row[0].strip()
        if not BikeAccident.objects.filter(case_number=int(case_number)):
            happened_at = parse_happened_at(row)
            violation_code = parse_violation_code(row)
            if violation_code:
                violation_code = get_violation(violation_code)
            primary_street, created = Street.objects.get_or_create(name=row[3].strip())
            cross_street, created = Street.objects.get_or_create(name=row[6].strip())
            feet_from_intersection = int(row[4])
            direction_from_intersection = directions.get(row[5], None)
            vehicle_one, created = Vehicle.objects.get_or_create(name=row[7].strip())
            if row[8].strip():
                vehicle_two, created = Vehicle.objects.get_or_create(name=row[8].strip())
            else: 
                vehicle_two = None
            if row[9].strip():
                vehicle_three, created = Vehicle.objects.get_or_create(name=row[9].strip())
            else: 
                vehicle_three = None
            number_injured = int(row[11])
            fatalities = int(row[12])
            hit_and_run = row[13] == 'YES'
            coordinates = locationutils.get_or_create("%s and %s, San Francisco, CA" % (primary_street.name, cross_street.name))
            b = BikeAccident(happened_at=happened_at, case_number=case_number, violation_code=violation_code, primary_street=primary_street,
                             cross_street=cross_street, feet_from_intersection=feet_from_intersection, direction_from_intersection=direction_from_intersection,
                             vehicle_one=vehicle_one, vehicle_two=vehicle_two, vehicle_three=vehicle_three, number_injured=number_injured,
                             fatalities=fatalities, hit_and_run=hit_and_run, coordinates=coordinates)
            b.save()
            
            if coordinates:
                client =  Client(settings.SIMPLEGEO_TOKEN, settings.SIMPLEGEO_SECRET)
                geo_context = client.context.get_context(formatted['latitude'], formatted['longitude'])
                neighborhood = tuple(f['name'] for f in geo_context['features'] if f['classifiers'][0]['category'] == 'Neighborhood') 
                neighborhood = neighborhood[0] if neighborhood else None
                city = tuple(f['name'] for f in geo_context['features'] if f['classifiers'][0]['category'] == 'City')
                city = city[0] if city else None
 
                row.append(neighborhood)
            else:
                row.append('')
            if b.violation_code: 
                row.append(b.violation_code.code)
                row.append(b.violation_code.title)
            writer.writerow(row)
            
            created=True
            if created:
                i += 1
                print "created id %s" %b.id
            else:
                j += 1
                print "could not create case # %s" % case_number
                
    print "\nFinished creating %s bike accidents" %i
    print "\nCould not create %s bike accidents" %j

def get_violation(code):
    try:
        v = ViolationCode.objects.get(code=code)
        if v:
            return v
    except:
        pass
    original_code = code
    if '.1' in code:
        code = code.replace('.1', '')
    url = base_url %code
    
    try:
        f = urllib2.urlopen(url)
        code_used = code
    except urllib2.HTTPError:
        try:
            again = base_url %re.sub("[^0-9]", "", code)
            if url != again:
                f = urllib2.urlopen(again)
                code_used = re.sub("[^0-9]", "", code)
            else:
                return None
        except urllib2.HTTPError:
            return None
    title, body = parseout(f.read())
    body = body.replace(code_used+'.', '')
    body = body.replace('&nbsp;', '')
    
    if not title:
        title = original_code
    
    v, created = ViolationCode.objects.get_or_create(code=original_code, defaults={'body': body, 'title': title, })
    if not created:
        v.body = body
        v.title = title
        v.save()
    return v

def parseout(html):
    soup = BeautifulSoup.BeautifulSoup(html)
    content = soup.findAll('div', attrs={'id': 'app_content'})
    if not content: return None
    content = content[0]
    ptags = []
    for p in content.findAll('p'):
        ptags.append("%s" %p)
    
    contents = "\n".join(ptags)
    title = content.findAll('h4')
    if title:
        title = title[0].text
    else:
        title = None
    body = CleanHtml(value=contents, tags_allowed=['p',]).clean()
    return (title, body)

def parse_happened_at(row):
    date_parts = row[1].split(" ")
    month = months.get(date_parts[1])
    day = date_parts[2][0:2]
    year = date_parts[2][3:7]
    hour = row[2][0:2]
    min = row[2][3:7]
    
    
    return datetime(int(year), int(month), int(day), int(hour), int(min), 0)

def parse_violation_code(row):
    return None if row[10].strip() in bad_violation_codes else row[10].strip()
