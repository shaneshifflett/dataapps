import os
import csv
from django.db.models import Sum, Count
from geopy import geocoders
from sfmayor2011.models import *
from locations.models import Coordinates
from datetime import datetime

def geocode_cities():
    cities = Contribution.objects.all().values_list('place__city', 'place__state').distinct()
    g = geocoders.Google()
    for c in cities:
        try:
            city = c[0]
            state = c[1]
            contribs = Contribution.objects.filter(place__city=city, place__state=state)
            place, (lat, lng) = g.geocode(city + ', ' + state)
            print 'place=%s lat=%s lng=%s' % (place, lat, lng)
            coords = Coordinates(latitude=lat, longitude=lng)
            coords.save()
            print coords.id
            for contrib in contribs:
                contrib.place.coordinates = coords
                contrib.place.save()
                contrib.save()
        except Exception as e:
            print e


def print_contribs():
    cities = Contribution.objects.all().values_list('place__city',\
     'place__state', 'place__coordinates')
    writer = csv.writer(open("%s/city_contrib_counts_dos.csv" %os.path.dirname(__file__), 'wb'), 
                           delimiter=',', quotechar='"')
    header = ['citystate','count','latlng']
    writer.writerow(header)
    for c in cities:
        city = c[0]
        state = c[1]
        amt = Contribution.objects.filter(place__city=city,\
         place__state=state).aggregate(Count('amount'))
        if amt != None and c[2] != None:
            coords = Coordinates.objects.get(id=c[2])
            dollar_amt = amt['amount__count']
            citystate = city+ ', ' + state
            latlng = '%s, %s' % (coords.latitude, coords.longitude)
            writer.writerow([citystate, dollar_amt, latlng])

def contributors():
    d = datetime(2011,3,1)
    bmarch_names = Contribution.objects.filter(candidate__entity__full_name__name='Bevan Dufty',\
     date__lte=d).exclude(amount__gt=200).values_list('contributor')
    afmarch_names = Contribution.objects.filter(candidate__entity__full_name__name='Bevan Dufty',\
     date__gt=d).values_list('contributor')
    intersection = filter(set(afmarch_names).__contains__, bmarch_names)
    before_total = 0
    after_total = 0
    for n in intersection:
        before_contrib = Contribution.objects.filter(contributor__id=n[0],\
         date__lte=d).aggregate(Sum('amount'))
        after_contrib = Contribution.objects.filter(contributor__id=n[0],\
         date__gt=d).aggregate(Sum('amount'))
        before_total += before_contrib['amount__sum']
        after_total += after_contrib['amount__sum']
    print after_total
    print before_total
