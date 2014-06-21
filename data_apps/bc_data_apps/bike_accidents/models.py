from django.db import models
from localflavor.us.models import PhoneNumberField
from django_extensions.db.fields import AutoSlugField
from data_apps.bc_apps.locations import utils as locationutils

class Street(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return unicode(self.name)


class FullAddress(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return unicode(self.name)

class Vehicle(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return unicode(self.name)

class Place(models.Model):
    #a city or a county name
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return unicode(self.name)


class LightingCondition(models.Model):
    #a city or a county name
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return unicode(self.name)

class RoadSurface(models.Model):
    #a city or a county name
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return unicode(self.name)

class ViolationCode(models.Model):
    code  = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self):
        return unicode(self.code + ' - ' + self.title)
    
class BikeAccident(models.Model):
    happened_at                 = models.DateTimeField(db_index=True)
    case_number                 = models.IntegerField()
    violation_code              = models.ForeignKey('bike_accidents.ViolationCode', null=True, blank=True)
    primary_street              = models.ForeignKey('bike_accidents.Street', related_name='primarystreet', null=True, blank=True)
    cross_street                = models.ForeignKey('bike_accidents.Street', related_name='cross_street', null=True, blank=True)
    full_address                = models.ForeignKey('bike_accidents.FullAddress', null=True, blank=True)
    feet_from_intersection      = models.DecimalField(max_digits=10, decimal_places=2)
    direction_from_intersection = models.CharField(choices=(('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')), null=True, blank=True, max_length=20)
    vehicle_one                 = models.ForeignKey('bike_accidents.Vehicle', related_name='vehicleone')
    vehicle_two                 = models.ForeignKey('bike_accidents.Vehicle', related_name='vehicletwo', blank=True, null=True)
    vehicle_three               = models.ForeignKey('bike_accidents.Vehicle', related_name='vehiclethree', blank=True, null=True)
    number_injured              = models.IntegerField(default=0)
    fatalities                  = models.IntegerField(default=0)
    hit_and_run                 = models.BooleanField(default=False)
    coordinates                 = models.ForeignKey('locations.Coordinates', blank=True, null=True)
    county                      = models.ForeignKey('bike_accidents.Place', related_name='county', blank=True, null=True)
    city                        = models.ForeignKey('bike_accidents.Place', related_name='city', blank=True, null=True)
    lighting                    = models.ForeignKey('bike_accidents.LightingCondition', blank=True, null=True)
    road_surface                = models.ForeignKey('bike_accidents.RoadSurface', blank=True, null=True)
    injured                     = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u'Accident on %s and %s' % (self.primary_street, self.cross_street)
    
class SubmittedBikeAccident(models.Model):
    Y_N_CHOICE = (('Y','Yes'),('N','No'))
    REPORT_STATUS_CHOICE = (
        ('1', 'No, I panicked and went home'),
        ('2', 'No, I didn\'t have insurance'),
        ('3', 'No, it wasn\'t a big deal'),
        ('5', 'No, other reason...'),
        ('4', 'Yes, it was reported'))
    NEXT_CHOICES = (
        ('1', 'I went home'),
        ('2', 'I went to the hospital'),
        ('3', 'I was sued'),
        ('4', 'I pressed charges'))

    HOUR_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
    )

    MINUTE_CHOICES = (
        ('0', '00'),
        ('5', '05'),
        ('10', '10'),
        ('15', '15'),
        ('20', '20'),
        ('25', '25'),
        ('30', '30'),
        ('35', '35'),
        ('40', '40'),
        ('45', '45'),
        ('50', '50'),
        ('55', '55'),
    )

    AM_PM_CHOICES = (
        ('AM', 'AM'),
        ('PM', 'PM'))

    name                        = models.CharField(max_length = 128)
    email                       = models.EmailField(max_length=255)
    phone                       = PhoneNumberField(null=True, blank=True,\
        verbose_name="Phone (ex: xxx-xxx-xxxx)")
    age                         = models.IntegerField()
    date                        = models.DateField(db_index=True)
    hour                        = models.CharField(max_length=2, default='1', choices=HOUR_CHOICES)
    minute                      = models.CharField(max_length=2, default='0', choices=MINUTE_CHOICES)
    ampm                        = models.CharField(max_length=2, default='AM',\
        choices=AM_PM_CHOICES, verbose_name='AM or PM?')
    primary_street              = models.CharField(max_length=255)
    cross_street                = models.CharField(max_length=255)
    city                        = models.CharField(max_length=255)
    zip_code                    = models.CharField(max_length=5)
    follow_up                   = models.CharField(max_length=1, default='Y',\
        choices=Y_N_CHOICE, verbose_name='Can we contact you for more information?')
    description                 = models.TextField(blank=True, null=True, \
        verbose_name="Please describe what happened")
    #end first form, required fields
    number_injured              = models.IntegerField(default=0, verbose_name=\
        "Number of people injured")
    fatalities                  = models.IntegerField(default=0, verbose_name=\
        "Number of people killed")
    hit_and_run                 = models.CharField(max_length=1, default='N',\
        choices=Y_N_CHOICE,\
        verbose_name="Was this a hit and run accident?")
    accident_cause              = models.TextField(blank=True, null=True,\
        verbose_name="Please tell us what caused the crash")
    #end second form, all optional fields
    injury_description          = models.TextField(blank=True, null=True,\
        verbose_name="Please tell us about any injuries you suffered")
    officially_reported         = models.CharField(max_length=4,\
        choices=REPORT_STATUS_CHOICE, null=True, blank=True,\
        verbose_name="Did you report the accident to authorities?")
    next_steps                  = models.CharField(max_length=1,\
        choices=NEXT_CHOICES, null=True, blank=True,\
        verbose_name="Tell us what you did next")
    accident_cost               = models.DecimalField(max_digits=13,\
        decimal_places=2, null=True, blank=True,\
        verbose_name="How much did this accident cost you (repairs, injury, legal, etc)")
    cost_description            = models.TextField(blank=True, null=True,\
        verbose_name="Please describe to us the cost breakdown of this accident")
    
    #no form input required
    coordinates                 = models.ForeignKey('locations.Coordinates', blank=True, null=True)
    
    def __unicode__(self):
        return u'Submitted Accident on %s and %s' % (self.primary_street, self.cross_street)

    def save(self):
        if not self.coordinates:
            coordinates = locationutils.get_or_create('%s and %s, %s, CA' % (self.primary_street, 
                                                                             self.cross_street, 
                                                                             self.city)) 
            if coordinates:
                self.coordinates = coordinates
        return super(SubmittedBikeAccident, self).save()
