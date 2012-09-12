import csv
import os
import random

from englewood import DotDensityPlotter
from sfmayor2011.models import Contribution, Place, Candidate

INPUT_PATH = '/vagrant/citizen/dataapps/sfmayor2011/data/shape_us_zipcodes/tl_2010_us_zcta510.shp'
INPUT_LAYER = 'tl_2010_us_zcta510'
OUTPUT_PATH = '/vagrant/output/'
OUTPUT_LAYER = 'dots'


places = Place.objects.all().values_list('zip').distinct()

contrib_zip_cnt = {}

candidates_list = Candidate.objects.all()

for p in places:
    for candidate in candidates_list:
        contribs = Contribution.objects.filter(place__zip=p[0], candidate=candidate)
        trimmed_zip = p[0].split('-')[0]#all zips are 5 digits
        if trimmed_zip in contrib_zip_cnt:
            candidate_cnt = contrib_zip_cnt[trimmed_zip]
            if candidate.entity.full_name.name in candidate_cnt:
                candidate_cnt[candidate.entity.full_name.name] += len(contribs)
            else:
                candidate_cnt[candidate.entity.full_name.name] = len(contribs)
            
            #contrib_zip_cnt[trimmed_zip] += len(contribs)
            #print 'added zip %s' % trimmed_zip
        else:
            candidate_cnt = {candidate.entity.full_name.name:len(contribs)}
            contrib_zip_cnt[trimmed_zip] = candidate_cnt
            #print 'created zip %s' % trimmed_zip


def get_data(feature):
    # The third column of the shapefile is the ward number
    zip_id = feature.GetField(1)

    # Get the correct ward data
    try:
        zip = contrib_zip_cnt[zip_id]
        count = 0
        for key in zip.keys():
            count += zip[key]
        print 'Processing zip=%s cnt=%s' % (zip_id, count)
    except KeyError:
        return None

    return zip
   

# Ensure the output path exists
if not os.path.exists(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)

# Create a map with one dot for every 25 people of each group
# Each dot will have an attribute 'GROUP' that will be one of
# 'asian', 'black', 'hispanic', or 'white'.
dots = DotDensityPlotter(INPUT_PATH, INPUT_LAYER, 'ESRI Shapefile', OUTPUT_PATH, OUTPUT_LAYER, get_data, 1)
dots.plot()
