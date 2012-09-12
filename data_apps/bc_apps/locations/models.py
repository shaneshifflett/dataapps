from django.conf import settings
from django.db import models

from django_extensions.db.fields import AutoSlugField, CreationDateTimeField, ModificationDateTimeField

LOCAL_COUNTY_SLUGS = ('alameda',
                      'contra-costa',
                      'marin',
                      'napa',
                      'san-francisco',
                      'san-mateo',
                      'santa-clara',
                      'solano',
                      'sonoma',) 

class State(models.Model):
    name = models.CharField(max_length=255, help_text=u'Maximum length of 255 characters')
    slug = AutoSlugField(populate_from=('name',))
    
    class Meta:
        ordering = ['name']
        
    def __unicode__(self):
        return u"%s" %self.name

class LocalCountyManager(models.Manager):
    """ Returns counties within the Bay Area"""

    def get_query_set(self):
        return super(LocalCountyManager, self).get_query_set().filter(slug__in=LOCAL_COUNTY_SLUGS)

class County(models.Model):
    name              = models.CharField(max_length=255, help_text=u'Maximum length of 255 characters')
    twitter_list_name = models.CharField(max_length=255, blank=True, null=True, help_text=u'Maximum length of 255 characters')
    twitter_user      = models.CharField(max_length=255, blank=True, null=True, help_text=u'Maximum length of 255 characters')
    twitter_list_id   = models.CharField(max_length=255, blank=True, null=True, help_text=u'Maximum length of 255 characters')
    slug              = AutoSlugField(populate_from=('name',))
    
    # Managers
    objects         = models.Manager()
    local_objects   = LocalCountyManager()
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Counties"
        
    def __unicode__(self):
        return u"%s" %self.name
    
    def cities(self):
        return City.objects.filter(county=self)

    @models.permalink
    def get_absolute_url(self):
        return ('locations_county', (self.slug,))

class LocalCityManager(models.Manager):
    """ Returns counties within the Bay Area"""

    def get_query_set(self):
        return super(LocalCityManager, self).get_query_set().filter(county__slug__in=LOCAL_COUNTY_SLUGS)

class City(models.Model):
    name   = models.CharField(max_length=255, help_text=u'Maximum length of 255 characters', db_index=True)
    slug   = AutoSlugField(populate_from=('name',))
    county = models.ForeignKey(County, blank=True, null=True)

    # Managers
    objects         = models.Manager()
    local_objects   = LocalCityManager()
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering            = ['name']
        
    def __unicode__(self):
        return u"%s" %self.name

    @models.permalink
    def get_absolute_url(self):
        return ('locations_city', (self.slug,))

class Neighborhood(models.Model):
    name = models.CharField(max_length=255, help_text=u'Maximum length of 255 characters')
    slug = AutoSlugField(populate_from=('name',))
    
    class Meta:
        ordering = ['name']
        
    def __unicode__(self):
        return u"%s" %self.name

class Coordinates(models.Model):
    latitude     = models.FloatField()
    longitude    = models.FloatField()
    neighborhood = models.ForeignKey(Neighborhood, blank=True, null=True)
    city         = models.ForeignKey(City, blank=True, null=True)
    county       = models.ForeignKey(County, blank=True, null=True)
    state        = models.ForeignKey(State, blank=True, null=True)
    search_query = models.CharField(max_length=255, null=True, blank=True, editable=False)
    notes        = models.CharField("What's Here?", max_length=255, null=True, blank=True)
    created_at   = CreationDateTimeField()
    updated_at   = ModificationDateTimeField()
    
    class Meta:
        ordering = ['-id']
        verbose_name_plural = "Coordinates"
        
    def __unicode__(self):
        return u"%s-%s" %(self.latitude, self.longitude)
    
    def placename(self):
        try:
            return self._placename
        except:
            place = ""
            if self.neighborhood:
                place = self.neighborhood.name
            if self.city:
                if place: place += ", "
                place += self.city.name
            if self.state:
                if place: place += ", "
                place += self.state.name
            self._placename = place
            return self._placename
        