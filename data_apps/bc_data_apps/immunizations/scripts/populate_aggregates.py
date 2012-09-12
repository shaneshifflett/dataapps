from django.db.models import Sum

from immunizations.models import IzCountyAggregate, IzCityAggregate, IzSchoolAggregate, IzDistrictAggregate, SchoolImmunization, Pertussis
from locations.models import County, City
from schools.models import SchoolDistrict, School
from settings import LOCAL_COUNTY_SLUGS

def aggregate_counties():
    counties = County.local_objects.all()
    for county in counties:
        try:
            ins = {}
            ins['county'] = county
            ins['enrollment'] = enrollment = SchoolImmunization.objects.filter(year=2010, school__county=county).aggregate(Sum('enrollment'))['enrollment__sum']
            ins['public_number'] = public_number = SchoolImmunization.objects.filter(year=2010, school__county=county, school__type='PU').aggregate(Sum('enrollment'))['enrollment__sum']
            ins['percent_public'] = (float(public_number) / float(enrollment)) * 100
            ins['private_number'] = private_number = SchoolImmunization.objects.filter(year=2010, school__county=county, school__type='PR').aggregate(Sum('enrollment'))['enrollment__sum']
            ins['percent_private'] = (float(private_number) / float(enrollment)) * 100
            ins['up_to_date_number'] = up_to_date_number = SchoolImmunization.objects.filter(year=2010, school__county=county).aggregate(Sum('up_to_date_number'))['up_to_date_number__sum']
            ins['pbe_number'] = pbe_number = SchoolImmunization.objects.filter(year=2010, school__county=county).aggregate(Sum('pbe_number'))['pbe_number__sum']
            ins['percent_up_to_date'] = (float(up_to_date_number) / float(enrollment)) * 100
            ins['percent_pbe'] = (float(pbe_number) / float(enrollment)) * 100
            ins['conditional_number'] = conditional_number = SchoolImmunization.objects.filter(year=2010, school__county=county).aggregate(Sum('conditional_number'))['conditional_number__sum']
            ins['percent_conditional'] = (float(conditional_number) / float(enrollment)) * 100
            p = Pertussis.objects.filter(county=county, year=2011)
            ins['pertussis_number'] = p[0].cases if p else 0
            ins['pertussis_rate'] = p[0].rate if p else 0
            
            IzCountyAggregate.objects.get_or_create(**ins)
        except Exception as e:
            import pdb; pdb.set_trace()
            print 'e=%s county=%s' % (e, county)

def run():
    
    counties = County.local_objects.all()
    for county in counties:
        try:
            ins = {}
            ins['county'] = county
            ins['enrollment'] = enrollment = SchoolImmunization.objects.filter(year=2010, school__county=county).aggregate(Sum('enrollment'))['enrollment__sum']
            ins['public_number'] = public_number = SchoolImmunization.objects.filter(year=2010, school__county=county, school__type='PU').aggregate(Sum('enrollment'))['enrollment__sum']
            ins['percent_public'] = (float(public_number) / float(enrollment)) * 100
            ins['private_number'] = private_number = SchoolImmunization.objects.filter(year=2010, school__county=county, school__type='PR').aggregate(Sum('enrollment'))['enrollment__sum']
            ins['percent_private'] = (float(private_number) / float(enrollment)) * 100
            ins['up_to_date_number'] = up_to_date_number = SchoolImmunization.objects.filter(year=2010, school__county=county).aggregate(Sum('up_to_date_number'))['up_to_date_number__sum']
            ins['pbe_number'] = pbe_number = SchoolImmunization.objects.filter(year=2010, school__county=county).aggregate(Sum('pbe_number'))['pbe_number__sum']
            ins['percent_up_to_date'] = (float(up_to_date_number) / float(enrollment)) * 100
            ins['percent_pbe'] = (float(pbe_number) / float(enrollment)) * 100
            ins['conditional_number'] = conditional_number = SchoolImmunization.objects.filter(year=2010, school__county=county).aggregate(Sum('conditional_number'))['conditional_number__sum']
            ins['percent_conditional'] = (float(conditional_number) / float(enrollment)) * 100
            p = Pertussis.objects.filter(county=county, year=2011)
            ins['pertussis_number'] = p[0].cases if p else 0
            ins['pertussis_rate'] = p[0].rate if p else 0
            
            IzCountyAggregate.objects.get_or_create(**ins)
        except Exception as e:
            print 'e=%s county=%s' % (e, county)
    
    cities = City.local_objects.all()
    for city in cities:
        ins = {}
        si = SchoolImmunization.objects.filter(year=2010, school__city=city)
        if si:
            ins['county'] = si[0].school.county
            ins['city'] = city
            ins['enrollment'] = enrollment = SchoolImmunization.objects.filter(year=2010, school__city=city).aggregate(Sum('enrollment'))['enrollment__sum']
            ins['public_number'] = public_number = SchoolImmunization.objects.filter(year=2010, school__city=city, school__type='PU').aggregate(Sum('enrollment'))['enrollment__sum'] or 0
            ins['percent_public'] = (float(public_number) / float(enrollment)) * 100
            ins['private_number'] = private_number = SchoolImmunization.objects.filter(year=2010, school__city=city, school__type='PR').aggregate(Sum('enrollment'))['enrollment__sum']  or 0
            ins['percent_private'] = (float(private_number) / float(enrollment)) * 100
            ins['up_to_date_number'] = up_to_date_number = SchoolImmunization.objects.filter(year=2010, school__city=city).aggregate(Sum('up_to_date_number'))['up_to_date_number__sum']
            ins['pbe_number'] = pbe_number = SchoolImmunization.objects.filter(year=2010, school__city=city).aggregate(Sum('pbe_number'))['pbe_number__sum']
            ins['percent_up_to_date'] = (float(up_to_date_number) / float(enrollment)) * 100
            ins['percent_pbe'] = (float(pbe_number) / float(enrollment)) * 100
            ins['conditional_number'] = conditional_number = SchoolImmunization.objects.filter(year=2010, school__city=city).aggregate(Sum('conditional_number'))['conditional_number__sum']
            ins['percent_conditional'] = (float(conditional_number) / float(enrollment)) * 100
            
            IzCityAggregate.objects.get_or_create(**ins)
    
    for si in SchoolImmunization.objects.filter(year=2010):
        ins = {}
        ins['city'] = si.school.city
        ins['school'] = si.school
        ins['district'] = si.school.district
        ins['type'] = si.school.type
        ins['enrollment'] = enrollment = si.enrollment
        ins['up_to_date_number'] = up_to_date_number = si.up_to_date_number
        ins['pbe_number'] = pbe_number = si.pbe_number
        ins['percent_up_to_date'] = (float(up_to_date_number) / float(enrollment)) * 100
        ins['percent_pbe'] = (float(pbe_number) / float(enrollment)) * 100
        ins['conditional_number'] = conditional_number = si.conditional_number
        ins['percent_conditional'] = (float(conditional_number) / float(enrollment)) * 100
        
        IzSchoolAggregate.objects.get_or_create(**ins)
    
    
    districts = SchoolDistrict.objects.all()
    for district in districts:
        ins = {}
        si = SchoolImmunization.objects.filter(year=2010, school__district=district)
        if si:
            ins['county'] = si[0].school.county
            ins['district'] = district
            ins['enrollment'] = enrollment = SchoolImmunization.objects.filter(year=2010, school__district=district).aggregate(Sum('enrollment'))['enrollment__sum']
            ins['up_to_date_number'] = up_to_date_number = SchoolImmunization.objects.filter(year=2010, school__district=district).aggregate(Sum('up_to_date_number'))['up_to_date_number__sum']
            ins['pbe_number'] = pbe_number = SchoolImmunization.objects.filter(year=2010, school__district=district).aggregate(Sum('pbe_number'))['pbe_number__sum']
            ins['percent_up_to_date'] = (float(up_to_date_number) / float(enrollment)) * 100
            ins['percent_pbe'] = (float(pbe_number) / float(enrollment)) * 100
            ins['conditional_number'] = conditional_number = SchoolImmunization.objects.filter(year=2010, school__district=district).aggregate(Sum('conditional_number'))['conditional_number__sum']
            ins['percent_conditional'] = (float(conditional_number) / float(enrollment)) * 100
            
            IzDistrictAggregate.objects.get_or_create(**ins)
    
