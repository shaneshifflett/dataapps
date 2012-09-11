from django.db import models

from django_extensions.db.fields import AutoSlugField, CreationDateTimeField, ModificationDateTimeField

class SchoolDistrict(models.Model):
    name    = models.CharField(max_length=255,)
    slug    = AutoSlugField(populate_from=('name',))
    body    = models.TextField(blank=True, null=True)

    created_at   = CreationDateTimeField()
    updated_at   = ModificationDateTimeField()
    
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('schools_districts_view', (self.slug,))

    class Meta:
        ordering            = ['name']

class School(models.Model):
    SCHOOL_TYPE_CHOICES = (
        ('PU', 'Public'),
        ('PR', 'Private'),
        ('CH', 'Charter'),
        ('MA', 'Magnet'),
        ('OT', 'Other')
    )

    name        = models.CharField(max_length=255,)
    slug        = AutoSlugField(populate_from=('name',))
    type        = models.CharField(max_length=2, choices=SCHOOL_TYPE_CHOICES)
    body        = models.TextField(blank=True, null=True)
    district    = models.ForeignKey('schools.SchoolDistrict', blank=True, null=True)
    city        = models.ForeignKey('locations.City', blank=True, null=True)
    county      = models.ForeignKey('locations.County', blank=True, null=True)

    created_at  = CreationDateTimeField()
    updated_at  = ModificationDateTimeField()

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('schools_view', (self.slug,))

    class Meta:
        ordering            = ['name']