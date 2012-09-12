import logging

from django.conf import settings
from django.template.defaultfilters import slugify

from geopy import geocoders
from simplegeo import Client

from data_apps.bc_apps.locations.models import State, County, City, Neighborhood, Coordinates

def get_or_create(q, notes=None):
    try:
        g = geocoders.Google('', output_format='json_unformatted')
        line = g.geocode(q, exactly_one=False)
        logging.debug('google returned: %s' %line)
        formatted = {}
        formatted['location'] = line.get('address')
        formatted['longitude'], formatted['latitude'] = line['Point']['coordinates'][:2]
        formatted['country'] = line['AddressDetails']['Country']['CountryName']
        try:
            formatted['county'] = line['AddressDetails']['Country']['AdministrativeArea']['SubAdministrativeArea']['SubAdministrativeAreaName']
        except:
            formatted['county'] = ""
        formatted['state'] = line['AddressDetails']['Country']['AdministrativeArea']['AdministrativeAreaName']
        try:
            formatted['city'] = line['AddressDetails']['Country']['AdministrativeArea']['SubAdministrativeArea']['Locality']['LocalityName']
        except:
            formatted['city'] = line['AddressDetails']['Country']['AdministrativeArea']['Locality']['LocalityName']
        
        if not formatted:
            return None
        
        if not formatted.get('latitude') or not formatted.get('longitude'):
            return None
        
        client =  Client(settings.SIMPLEGEO_TOKEN, settings.SIMPLEGEO_SECRET)
        geo_context = client.context.get_context(formatted['latitude'], formatted['longitude'])
        neighborhood = tuple(f['name'] for f in geo_context['features'] if f['classifiers'][0]['category'] == 'Neighborhood') 
        neighborhood = neighborhood[0] if neighborhood else None
        city = tuple(f['name'] for f in geo_context['features'] if f['classifiers'][0]['category'] == 'City')
        city = city[0] if city else None
            
        
        coo = Coordinates.objects.filter(latitude=formatted.get('latitude'), longitude=formatted.get('longitude'))
    
        #we do all of the following in order to get notes, if any
        
        if formatted.get('state'):
            try:
                state = State.objects.get(slug=slugify(formatted['state']))
                coo.filter(state=state)
            except:
                state = None
        
        cty = city or formatted.get('city')
        if cty:
            try:
                city = City.objects.get(slug=slugify(city))
                coo.filter(city=city)
            except:
                city = None
                
        if formatted.get('county'):
            try:
                county = County.objects.get(slug=slugify(formatted['county']))
                coo.filter(county=county)
            except:
                county=None
        else:
            if cty and formatted.get('state'):
                found = Coordinates.objects.filter(city__name=cty, state__name=formatted.get('state'))
                for row in found:
                    if row.county:
                        county = row.county
                        break
        
        if neighborhood:
            try:
                neighborhood = Neighborhood.objects.get(slug=slugify(neighborhood))
                coo.filter(neighborhood=neighborhood)
            except:
                neighborhood = None
    
        if coo:
            if notes and not coo[0].notes:
                coo[0].notes = notes
                coo[0].save()
            return coo[0]
        else:
            c = {
                 'latitude': formatted.get('latitude'),
                 'longitude': formatted.get('longitude'),
                 'neighborhood': neighborhood,
                 'city': city,
                 'county': county,
                 'state': state,
                 'search_query': q,
                 'notes': notes,
            }
         
        coordinates = Coordinates(**c)
        coordinates.save()
        return coordinates
    except Exception as e:
        return None
    
