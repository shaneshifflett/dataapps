from immunizations.models import ImmunizationRaw, SchoolImmunization
from schools.models import School, SchoolDistrict
from locations.models import City, County

COUNTIES = (
    'ALAMEDA',
    'CONTRA COSTA',
    'MARIN',
    'NAPA',
    'SAN FRANCISCO',
    'SAN MATEO',
    'SANTA CLARA',
    'SOLANO',
    'SONOMA',
)

def districts():
    districts = ImmunizationRaw.objects.all().values_list('school_district').distinct()
    for d in districts:
        SchoolDistrict(name=d[0]).save()

def counties():
    counties = ImmunizationRaw.objects.all().values_list('county').distinct()
    for c in counties:
        try:
            county = County.objects.get(name__iexact=c[0])
        except Exception as e:
            County(name=c[0]).save()

def remove_dupes():
    print 'going thru counties'
    counties = ImmunizationRaw.objects.all().values_list('county').distinct()
    for c in counties:
        zz = County.objects.filter(name__iexact=c[0])
        if len(zz) > 1:
            for z in zz[1:]:
                print z.name 
                z.delete()
    print 'going thru cities'
    cities = ImmunizationRaw.objects.all().values_list('city').distinct()
    for c in cities:
        zz = City.objects.filter(name__iexact=c[0])
        if len(zz) > 1:
            for z in zz[1:]:
                print z.name
                z.delete()

def cities():
    cities = ImmunizationRaw.objects.all().values_list('city', 'county').distinct()
    for c in cities:
        try:
            city = City.objects.get(name__iexact=c[0])
        except:
            print 'couldnt find city=%s' % c[0]
            county = County.objects.get(name__iexact=c[1])
            City(name=c[0], county=county).save()

def schools():
    schools = ImmunizationRaw.objects.all().values_list('school_name',\
     'school_district', 'city', 'county').distinct()
    for s in schools:
        try:
            d = SchoolDistrict.objects.get(name=s[1])
            city = City.objects.get(name__iexact=s[2])
            county = County.objects.get(name__iexact=s[3])
            School(name=s[0], type='PU', district=d, city=city, county=county).save()
        except Exception as e:
            print 'e=%s district=%s city=%s county=%s school=%s' % (e, s[1], s[2], s[3], s[0])

def run():
    """
    Populate schools from immunization data
    """
    for im in ImmunizationRaw.objects.all():
        if im.county in COUNTIES:
            try:
                school = School.objects.filter(name=im.school_name, 
                                            county__name=im.county)
                if school:
                    school = school[0]
                SchoolImmunization(school=school, 
                                   year=im.year, 
                                   enrollment=im.enrollment,
                                   up_to_date_number=im.up_to_date_number,
                                   up_to_date_percent=im.up_to_date_percent,
                                   conditional_number=im.conditional_number,
                                   conditional_percent=im.conditional_percent,
                                   pbe_number=im.pbe_number,
                                   pbe_percent=im.pbe_percent,
                                   dtp4_number=im.dtp4_number,
                                   dtp4_percent=im.dtp4_percent,
                                   mmr1_number=im.mmr1_number,
                                   mmr1_percent=im.mmr1_percent,
                                   mmr2_number=im.mmr2_number,
                                   mmr2_percent=im.mmr2_percent,
                                   vari1_number=im.vari1_number,
                                   vari1_percent=im.vari1_percent).save()
            except Exception as e:
                print 'e=%s im=%s' % (e, im)
