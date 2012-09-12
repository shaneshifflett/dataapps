from django.db import models
from django.db.models import Sum
from django.db.models import Q
from django_extensions.db.fields import AutoSlugField
from django.contrib.localflavor.us.models import PhoneNumberField
from images.models import Image
from datetime import datetime

class Topic(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = AutoSlugField(populate_from=('name',))

    def __unicode__(self):
        return unicode(self.name)

class Poll(models.Model):
    """
    an object to encapsulate all the candidates and their rankings for a poll
    """
    source = models.ForeignKey('sfmayor2011.Entity', null=False, blank=False)
    url = models.URLField(max_length=200, blank=True, null=True)
    date = models.DateField(db_index=True)
    
    def __unicode__(self):
        return self.source.full_name.name + ' ' + str(self.date)

class URL(models.Model):
    """
    wrapper for a url to facilitate m2m relationships
    """
    description = models.CharField(max_length=255)
    url = models.URLField(max_length=200, blank=False, null=False)

class PollRanking(models.Model):
    poll = models.ForeignKey('sfmayor2011.Poll', blank=False, null=False)
    candidate = models.ForeignKey("sfmayor2011.Candidate", blank=True, null=True)
    percentile = models.IntegerField()

    def __unicode__(self):
        return self.candidate.entity.full_name.name + ' Poll:' + self.poll.source.full_name.name

class Name(models.Model):
    """
    a class to define names so we can store lists of names for more flexible
    name lookups
    """
    name = models.CharField(max_length=255, unique=True)
    slug = AutoSlugField(populate_from=('name',))

    def __unicode__(self):
        return self.name

class Entity(models.Model):
    """
    entity is unique person place or thing that will serve as a filter function
    as we load new data sets in and desire to trace everything to an entity
    """
    full_name = models.ForeignKey('sfmayor2011.Name', related_name='entity_full_name')
    last_name = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.ForeignKey('sfmayor2011.Place', null=True, blank=True)

    def __unicode__(self):
        return unicode(self.full_name.name)

class CandidateAlias(models.Model):
    alias = models.ForeignKey('sfmayor2011.Name', related_name='alias_name')
    candidate = models.ForeignKey('sfmayor2011.Candidate')

class Contribution(models.Model):
    contributor = models.ForeignKey('sfmayor2011.Entity', null=True, blank=True)
    candidate = models.ForeignKey('sfmayor2011.Candidate', null=True, blank=True)
    employer = models.ForeignKey('sfmayor2011.Name', null=True, blank=True, related_name='contribution_employer')
    occupation = models.ForeignKey('sfmayor2011.Name', null=True, blank=True, related_name='contribution_occupation')
    place = models.ForeignKey('sfmayor2011.Place', null=True, blank=True, related_name='contribution_place')
    amount = models.DecimalField(decimal_places=2, max_digits=11)
    date = models.DateTimeField(db_index=True)

class Place(models.Model):
    name = models.ForeignKey('sfmayor2011.Name', null=True, blank=True)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip = models.CharField(max_length=255, null=True, blank=True)
    coordinates = models.ForeignKey('locations.Coordinates', blank=True, null=True)

    def __unicode__(self):
        if self.name != None:
            return unicode('%s: %s %s, %s %s' % (self.name.name, self.street, self.city, self.state, self.zip))
        else:
            return unicode('%s %s, %s %s' % (self.street, self.city, self.state, self.zip))

class Event(models.Model):
    name = models.CharField(max_length=255)
    place = models.ForeignKey('sfmayor2011.Place', blank=False, null=False)
    date = models.DateField(db_index=True)
    candidate = models.ForeignKey('sfmayor2011.Candidate', blank=False, null=False)


class ContentCandidateRelation(models.Model):
    """
    Store the relationship of candidates mentioned in articles after performing full
    text searches of all content
    """
    article = models.ForeignKey('content.Content', blank=False, null=False)
    candidate = models.ForeignKey('sfmayor2011.Candidate', blank=False, null=False)
    

class Candidate(models.Model):
    entity = models.ForeignKey('sfmayor2011.Entity')
    topics = models.ManyToManyField('sfmayor2011.Topic', symmetrical=False, null=True, blank=True) 
    title = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ForeignKey('images.Image', null=True, blank=True)
    bio_photo = models.ForeignKey('images.Image', related_name='bio_photo', null=True, blank=True)
    bio = models.TextField(blank=True)
    age = models.CharField(max_length=2, default='99')
    hometown = models.CharField(max_length=255, default='Default City')
    party = models.CharField(max_length=255, default='Always party')
    website = models.URLField(max_length=200, blank=True, null=True)
    #surprise fact and photo relation
    address = models.ForeignKey("sfmayor2011.Place", null=True, blank=True)
    events = models.ManyToManyField('sfmayor2011.Event', related_name='candidate_events', symmetrical=False, null=True, blank=True)
    public_financing = models.DecimalField(decimal_places=2, max_digits=11, null=True, blank=True, default=0)
    other_financing = models.DecimalField(decimal_places=2, max_digits=11, null=True, blank=True, default=0)

    updated_at = models.DateTimeField(editable=False, blank=True, db_index=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    twitter = models.URLField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now() 
        super(Candidate, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.entity.full_name.name)

    def get_name(self):
        return self.entity.full_name.name

    def get_total_contributions(self):
        total = str(self.public_financing + self.other_financing)
        from django.contrib.humanize.templatetags.humanize import intcomma
        return "%s" % intcomma(total)

    def get_recent_poll(self):
        r = PollRanking.objects.filter(candidate=self).order_by('-poll__date')
        if len(r) > 0:
            return r[0].percentile


def get_candidates_w_bios():
    return Candidate.objects.all().exclude(Q(bio='')|Q(bio=None)|Q(bio=\
     'test bio zzzz')).order_by('entity__full_name__name')


class AskACandidate(models.Model):
    name = models.CharField(max_length=255)
    candidate = models.ForeignKey('sfmayor2011.Candidate', null=True, blank=True)
    email = models.EmailField(max_length=255)
    phone = PhoneNumberField(null=True, blank=True,\
        verbose_name="Phone (optional)")
    description = models.TextField(blank=False, null=False, \
        verbose_name="Your question")

    def get_candidate_name(self):
        if self.candidate == None:
            return 'All'
        else:
            return self.candidate.entity.full_name.name


def get_candidate_by_alias(alias):
    try:
        name, created = Name.objects.get_or_create(name=alias)
        alias_o = CandidateAlias.objects.get(alias=name)
        return alias_o.candidate
    except:
        return None

def get_or_create_alias(alias, candidate):
    name, created = Name.objects.get_or_create(name=alias)
    alias, created = CandidateAlias.objects.get_or_create(alias=name, candidate=candidate)
    return alias

def get_or_create_candidate(name):
    c_name, created = Name.objects.get_or_create(name=name)
    c_entity, created = Entity.objects.get_or_create(full_name=c_name)
    obj, created = Candidate.objects.get_or_create(entity=c_entity)
    return obj
