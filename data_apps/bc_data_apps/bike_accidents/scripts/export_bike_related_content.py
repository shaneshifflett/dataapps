import csv, cStringIO, codecs, os

from content.models import Content
from topics.models import Topic
from bike_accidents.models import *
from bike_accidents.views import COUNTIES

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def run():
    writer = UnicodeWriter(open("%s/../files/bike_related_content.csv" %os.path.dirname(__file__), 'wb'), 
                           encoding='utf-8', delimiter=',', quotechar='"')
    t = Topic.objects.get(slug='transportation')
    b = Topic.objects.get(slug='bikes')
    bike_content = Content.published_objects.filter(classname__in=['stories.story', 'blogs.post', 'columns.column'],
                                                    topics__in=[t,b], 
                                                    coordinates__isnull=False, 
                                                    pub_date__year=2010,)
   
    header = ['Title', 'URL', 'Deck', 'PubDate', 'icon', 'Latitude', 'Longitude'] 
    writer.writerow(header)
    for bc in bike_content:
        print bc
        writer.writerow([bc.title, bc.get_absolute_url(), bc.subscript if bc.subscript else '', bc.pub_date.strftime('%m/%d/%Y'), u'wht_pushpin', unicode(bc.coordinates.latitude), unicode(bc.coordinates.longitude)])

def get_intersection_counts():
    writer = UnicodeWriter(open("%s/../files/bike_accident_intersection_counts.csv" %os.path.dirname(__file__), 'wb'), 
                           encoding='utf-8', delimiter=',', quotechar='"')

    places = Place.objects.filter(name__in=COUNTIES.keys())
    intersections = {}
    for place in places:
        accidents = BikeAccident.objects.filter(county=place)
        for a in accidents:
            interxn = frozenset([a.primary_street, a.cross_street, a.city])
            if intersections.has_key(interxn):
                intersections[interxn].append(a)
            else:
                intersections[interxn] = [a]
    for k,v in intersections.items():
        #import pdb; pdb.set_trace()
        #print 'list=%s counts=%s' % (zzz, len(v))
        writer.writerow([v[0].primary_street.name, v[0].cross_street.name, v[0].city.name, v[0].county.name, str(len(v))])
