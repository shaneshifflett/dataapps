from django.db import models
from data_apps.bc_apps.schools.models import School

class ImmunizationRaw(models.Model):
    year = models.IntegerField(null=True, blank=True)
    county = models.CharField(max_length=255)
    public = models.CharField(max_length=255)
    school_district = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    school_name = models.CharField(max_length=255)
    enrollment = models.IntegerField()
    up_to_date_number = models.IntegerField()
    up_to_date_percent = models.IntegerField()
    conditional_number = models.IntegerField()
    conditional_percent = models.IntegerField()
    pbe_number = models.IntegerField()
    pbe_percent = models.IntegerField()
    dtp4_number = models.IntegerField()
    dtp4_percent = models.IntegerField()
    mmr1_number = models.IntegerField()
    mmr1_percent = models.IntegerField()
    mmr2_number = models.IntegerField()
    mmr2_percent = models.IntegerField()
    vari1_number = models.IntegerField()
    vari1_percent = models.IntegerField()

    def __unicode__(self):
        return u'%s Immunization %s' % (self.school_name, self.up_to_date_percent)

class SchoolImmunization(models.Model):
    school = models.ForeignKey('schools.School')
    year = models.IntegerField()
    enrollment = models.IntegerField()
    up_to_date_number = models.IntegerField()
    up_to_date_percent = models.IntegerField()
    conditional_number = models.IntegerField()
    conditional_percent = models.IntegerField()
    pbe_number = models.IntegerField()
    pbe_percent = models.IntegerField()
    dtp4_number = models.IntegerField()
    dtp4_percent = models.IntegerField()
    mmr1_number = models.IntegerField()
    mmr1_percent = models.IntegerField()
    mmr2_number = models.IntegerField()
    mmr2_percent = models.IntegerField()
    vari1_number = models.IntegerField()
    vari1_percent = models.IntegerField()
    
    def __unicode__(self):
        return u'%s Immunization %s' % (self.school.name, self.up_to_date_percent)

class IzCountyAggregate(models.Model):
    county = models.ForeignKey('locations.County')
    enrollment = models.IntegerField()
    public_number = models.IntegerField()
    percent_public = models.FloatField(null=True, blank=True)
    private_number = models.IntegerField()
    percent_private = models.FloatField(null=True, blank=True)
    up_to_date_number = models.IntegerField()
    percent_up_to_date = models.FloatField(null=True, blank=True)
    conditional_number = models.IntegerField()
    percent_conditional = models.IntegerField()
    pbe_number = models.IntegerField()
    percent_pbe = models.FloatField(null=True, blank=True)
    pertussis_number = models.IntegerField(null=True, blank=True, default=0)
    pertussis_rate = models.FloatField(null=True, blank=True)

class IzCityAggregate(models.Model):
    county = models.ForeignKey('locations.County')
    city = models.ForeignKey('locations.City')
    enrollment = models.IntegerField()
    public_number = models.IntegerField(null=True, blank=True)
    percent_public = models.FloatField(null=True, blank=True)
    private_number = models.IntegerField(null=True, blank=True)
    percent_private = models.FloatField(null=True, blank=True)
    up_to_date_number = models.IntegerField(null=True, blank=True)
    percent_up_to_date = models.FloatField(null=True, blank=True)
    conditional_number = models.IntegerField()
    percent_conditional = models.IntegerField()
    pbe_number = models.IntegerField(null=True, blank=True)
    percent_pbe = models.FloatField(null=True, blank=True)

class IzSchoolAggregate(models.Model):
    city = models.ForeignKey('locations.City', null=True, blank=True)
    school = models.ForeignKey('schools.School')
    district = models.ForeignKey('schools.SchoolDistrict', null=True, blank=True)
    type = models.CharField(max_length=2, choices=School.SCHOOL_TYPE_CHOICES)
    enrollment = models.IntegerField()
    up_to_date_number = models.IntegerField(null=True, blank=True)
    percent_up_to_date = models.FloatField(null=True, blank=True)
    conditional_number = models.IntegerField()
    percent_conditional = models.IntegerField()
    pbe_number = models.IntegerField(null=True, blank=True)
    percent_pbe = models.FloatField(null=True, blank=True)

class IzDistrictAggregate(models.Model):
    county = models.ForeignKey('locations.County', null=True, blank=True)
    district = models.ForeignKey('schools.SchoolDistrict', null=True, blank=True)
    enrollment = models.IntegerField()
    up_to_date_number = models.IntegerField(null=True, blank=True)
    percent_up_to_date = models.FloatField(null=True, blank=True)
    conditional_number = models.IntegerField()
    percent_conditional = models.IntegerField()
    pbe_number = models.IntegerField(null=True, blank=True)
    percent_pbe = models.FloatField(null=True, blank=True)

class Pertussis(models.Model):
    county = models.ForeignKey('locations.County')
    year   = models.IntegerField()
    cases  = models.IntegerField(verbose_name="Number of Cases")
    rate   = models.FloatField(verbose_name=u"Rate Per 100,000")
    
    def __unicode__(self):
        return u'%s - %s - %s' %(self.county.name, self.year, self.cases)
