from django.db import models

# Create your models here.

from django_extensions.db.fields import AutoSlugField

class GeoFileMapping(models.Model):
    logrecno = models.CharField(max_length=7)
    name = models.CharField(max_length=255)
    summary_level = models.CharField(max_length=3)
    state_code = models.CharField(max_length=2)
    county_code = models.CharField(max_length=3, blank=True)
    place_code =  models.CharField(max_length=5, blank=True)
    state_legislative_upper_code =  models.CharField(max_length=3, blank=True)
    state_legislative_lower_code =  models.CharField(max_length=3, blank=True)
    congressional_code = models.CharField(max_length=2, blank=True)
    tract_code = models.CharField(max_length=6, blank=True)

class GeographyType(models.Model):
    name = models.CharField(max_length=64)
    slug = AutoSlugField(populate_from=('name',))

    def __unicode__(self):
        return self.name

class CensusGeography(models.Model):
    #could be an id for a tract, legislative district, county, or place
    #not necesarily unique, combo of geotype and geoid are only unique pairs
    geo_id = models.CharField(max_length=20)
    geo_type = models.ForeignKey('census2010.GeographyType')
    display_name = models.CharField(max_length=255, null=False)
    info_text = models.text = models.TextField(blank=True)
    slug = AutoSlugField(populate_from=('display_name',))
    #only populated for cities and legilative districts
    intersecting_geos = models.ManyToManyField("self", symmetrical=False, null=True)
    #TODO: get_percent differences for all rows associated with each table between 2000 & 2010d
    def __unicode__(self):
        return self.display_name
    @models.permalink
    def get_absolute_url(self):
        if self.geo_type.name == "place":
            return ('census2010_city_detail', (), {'slug':self.slug})
        elif self.geo_type.name == "county":
            return ('census2010_county_detail', (), {'slug':self.slug})
        elif self.geo_type.name == "legislative_lower":
            return ('census2010_assembly_detail', (), {'slug':self.slug})
        elif self.geo_type.name == "legislative_upper":
            return ('census2010_senate_detail', (), {'slug':self.slug})
        elif self.geo_type.name == 'tract':
            return ('census2010_tract_detail', (), {'slug':self.slug})
        elif self.geo_type.name == 'congressional':
            return ('census2010_congressional_detail', (), {'slug':self.slug})
    def geo_list(self):
        return self.intersecting_geos.all()

class CensusTableRow(models.Model):
    TABLE_NAMES = (
        ('race','race'),
        ('hispanic','hispanic'),
        ('agerace','race over 18'),#over18
        ('agehispanic','hispanic over 18'))#over18 and hispanic

    YEAR_CHOICES = (
        ('2000','2000'),
        ('2000','2010'))

    table_year = models.CharField(max_length=4, null=False, choices=YEAR_CHOICES)
    table_name = models.CharField(max_length=32, choices=TABLE_NAMES)
    geography = models.ForeignKey('census2010.CensusGeography', null=False)
    #every instance of this class with the same geography populates this field with the same value
    #it is the total population of the geography
    total_population = models.PositiveIntegerField()
    total_population_one_race = models.PositiveIntegerField()
    total_white = models.PositiveIntegerField()
    total_black = models.PositiveIntegerField()
    total_indian = models.PositiveIntegerField()
    total_asian = models.PositiveIntegerField()
    total_islander = models.PositiveIntegerField()
    total_other = models.PositiveIntegerField()
    total_two_races = models.PositiveIntegerField(null=True)
    total_population_two_races = models.PositiveIntegerField(null=True)
    #only additional fields in the hispanic tables
    total_hispanic = models.PositiveIntegerField(null=True)
    total_not_hispanic = models.PositiveIntegerField(null=True)

class CensusTableP5Row(models.Model):
    year = models.IntegerField()
    geo_id = models.CharField(max_length=20)
    total = models.PositiveIntegerField()
    white = models.PositiveIntegerField()
    black = models.PositiveIntegerField()
    indian = models.PositiveIntegerField()
    asian = models.PositiveIntegerField()
    hawaiin = models.PositiveIntegerField()
    other = models.PositiveIntegerField()
    hispanic = models.PositiveIntegerField()

class CensusTableP12Row(models.Model):
    year = models.IntegerField()
    geo_id = models.CharField(max_length=20)
    total = models.PositiveIntegerField()
    male = models.PositiveIntegerField()
    female = models.PositiveIntegerField()
    male_under_18 = models.PositiveIntegerField()
    male_18_24 = models.PositiveIntegerField()
    male_25_29 = models.PositiveIntegerField()
    male_30_34 = models.PositiveIntegerField()
    male_35_39 = models.PositiveIntegerField()
    male_40_49 = models.PositiveIntegerField()
    male_50_59 = models.PositiveIntegerField()
    male_60_84 = models.PositiveIntegerField()
    male_85_plus = models.PositiveIntegerField()

    female_under_18 = models.PositiveIntegerField()
    female_18_24 = models.PositiveIntegerField()
    female_25_29 = models.PositiveIntegerField()
    female_30_34 = models.PositiveIntegerField()
    female_35_39 = models.PositiveIntegerField()
    female_40_49 = models.PositiveIntegerField()
    female_50_59 = models.PositiveIntegerField()
    female_60_84 = models.PositiveIntegerField()
    female_85_plus = models.PositiveIntegerField()
