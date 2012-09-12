import csv, cStringIO, codecs, os

from bike_accidents.models import SubmittedBikeAccident
from bike_accidents.models import ViolationCode

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
    writer = UnicodeWriter(open("%s/../files/user_reports.csv" %os.path.dirname(__file__), 'wb'), 
                           encoding='utf-8', delimiter=',', quotechar='"')
    submissions = SubmittedBikeAccident.objects.all()

    header = ['Date','Time','Street1', 'Street2', 'City', 'P1', 'P2', 'Inj', 'Fatal', 'HR'] 
    writer.writerow(header)
    for s in submissions:
        print s 
        writer.writerow([s.happened_at.strftime('%m/%d/%Y'), 
                         s.happened_at.strftime('%H:%I'),
                         s.primary_street.name, 
                         s.cross_street.name,
                         s.city.name, 
                         s.vehicle_one.name,
                         s.vehicle_two.name,
                         unicode(s.number_injured),
                         unicode(s.fatalities),
                         unicode(s.hit_and_run)])

def export_violation_codes():
    writer = UnicodeWriter(open("%s/../files/violation_codes.csv" %os.path.dirname(__file__), 'wb'), 
                           encoding='utf-8', delimiter=',', quotechar='"')

    violations = ViolationCode.objects.all()
    header = ['code', 'title', 'body']
    writer.writerow(header)
    for vc in violations:
        writer.writerow([unicode(vc.code), unicode(vc.title), unicode(vc.body)])
