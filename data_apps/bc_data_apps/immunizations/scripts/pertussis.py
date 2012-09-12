import csv, os

from django.core.exceptions import ObjectDoesNotExist

from locations.models import County
from immunizations.models import Pertussis

COUNTIES = (
    'alameda',
    'contra costa',
    'marin',
    'napa',
    'san francisco',
    'san mateo',
    'santa clara',
    'solano',
    'sonoma',
)


schools = []
districts = []
states = []
counties = {}

def run():
    contents = csv.reader(open("%s/../files/pertussis.csv" %os.path.dirname(__file__)), dialect='excel', delimiter=',', quotechar='"')
    contents.next()
    for row in contents:
        if not row[0].lower() in COUNTIES: print "nope! %s" %row[0] 
        county = County.objects.get(name__iexact=row[0].lower())
        cases2009 = int(row[1])
        rate2009 = float(row[2])
        cases2010 = int(row[3])
        rate2010 = float(row[4])
        Pertussis(county=county, year=2009, rate=rate2009, cases=cases2009).save()
        Pertussis(county=county, year=2010, rate=rate2010, cases=cases2010).save()

def run_2011():
    contents = csv.reader(open("%s/../files/pertussis2011.csv" %os.path.dirname(__file__)), dialect='excel', delimiter=',', quotechar='"')
    contents.next()
    for row in contents:
        if not row[0].lower() in COUNTIES: print "nope! %s" %row[0] 
        county = County.objects.get(name__iexact=row[0].lower())
        cases2009 = int(row[1])
        rate2009 = float(row[2])
        cases2010 = int(row[3])
        rate2010 = float(row[4])
        Pertussis(county=county, year=2010, rate=rate2009, cases=cases2009).save()
        Pertussis(county=county, year=2011, rate=rate2010, cases=cases2010).save()
