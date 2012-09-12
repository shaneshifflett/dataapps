from django.db import models
from django_extensions.db.fields import AutoSlugField
from collections import deque
from sets import Set


class NameValuePair(models.Model):
    """
    store slate counts or candidate count pairs 
    """
    name = models.CharField(max_length=750)
    value_one = models.PositiveIntegerField()
    value_two = models.PositiveIntegerField(null=True, blank=True)


class ExhaustedBallotException(Exception):
    """
    class to indicate all choices on this ballot have been used
    """
    pass

class OverVoteException(Exception):
    """
    class to signify more than one vote was cast for this ballot on this round
    """
    pass

class UnderVoteException(Exception):
    """
    class to signal when no vote was cast for this ballot on this round
    """
    pass


class Race(models.Model):
    date = models.DateField(db_index=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    type = models.CharField(max_length=255)
    votes = models.ManyToManyField('rankedvotes.RankedBallot', symmetrical=False, null=True, blank=True, related_name='race_votes')
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name',))
    text = models.TextField(null=True, blank=True)
    headline = models.CharField(max_length=255)
    deck = models.CharField(max_length=255)
    disclaimer = models.TextField(null=True, blank=True)


    def __str__(self):
        return '%s' %self.name

    def __unicode__(self):
        return u'%s'%(self.__str__())

    def get_total_ballots(self):
        try:
            return self._total_ballots
        except:
            self._total_ballots = RankedBallot.objects.filter(race=self).exclude(choice_one__isnull=True, choice_two__isnull=True, choice_three__isnull=True).count()
            return self._total_ballots

    def get_ballots_to_process(self):
        try:
            return self._processing_ballots
        except:
            self._processing_ballots = RankedBallot.objects.filter(race=self)
            return self._processing_ballots

    def get_ballots_cnt(self):
        try:
            return self._ballot_cnt
        except:
            self._ballot_cnt = RankedBallot.objects.filter(race=self).count()
            return self._ballot_cnt


class Candidate(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name',))
    race = models.ForeignKey('rankedvotes.Race', blank=False, null=False)

    def __unicode__(self):
        return unicode(self.name)

class PrecinctAnalysis(models.Model):
    #store me in boundary_db
    #can't story fk reference to race bc it's on master ! boundary_db
    race_name = models.CharField(max_length=255)
    precinct = models.CharField(max_length=255)
    total = models.IntegerField()
    exhausted = models.IntegerField()
    one_unique = models.IntegerField()
    two_unique = models.IntegerField()
    three_unique = models.IntegerField()

    undervotes = models.IntegerField()
    overvotes = models.IntegerField()

    #num of ballots w/ duplicate choices
    duplicates = models.IntegerField()
    #num of ballots w/ one or more blank choices
    blanks = models.IntegerField()
    #store cnt of 1st place votes for the winner 
    first_choice = models.IntegerField()


    slate_counts = models.ManyToManyField('rankedvotes.NameValuePair', symmetrical=False, null=True, blank=True,related_name='namevalue_slates')
    candidate_counts = models.ManyToManyField('rankedvotes.NameValuePair', symmetrical=False, null=True, blank=True,related_name='namevalue_candidates')
    
    def get_candidate_rankings(self):
        try:
            return self.candidate_counts_list
        except:
            candidate_counts_list = list()
            for nvp in self.candidate_counts.all():
                candidate_counts_list.append([nvp.name, nvp.value_one, nvp.value_two])
            self.candidate_counts_list = candidate_counts_list
            return self.candidate_counts_list

    def get_common_slates(self):
        try:
            return self.common_slates_list
        except:
            self.common_slates_list = list()
            for nvp in self.slate_counts.all():
                self.common_slates_list.append([nvp.name, nvp.value_one])
            return self.common_slates_list
  

class OverUnderCandidates:
    '''
    Singleton class to increase performance by
    only querying for over/undervote candidates once
    
    There is an over/undervote candidate pair for every race
    All ballots for a race should only have to access the db once for either over/undervote candidate
    W/o this Singleton we would have to modify this file to set the race for the over/undervote candidate
    else every instance of RankedBallot would have its own instance of an over/undervote candidate
    '''

    class __impl:
        """ Implementation of the singleton interface """

        def overvote_c(self):
            return self.__overvote_c

        def undervote_c(self):
            return self.__undervote_c

    __instance = None
    __undervote_c = None
    __overvote_c = None

    def __init__(self,race):
        """ Create singleton instance """
        # Check whether we already have an instance
        if OverUnderCandidates.__instance is None:
            # Create and remember instance
            OverUnderCandidates.__instance = OverUnderCandidates.__impl()
            OverUnderCandidates.__undervote_c = Candidate.objects.get(race=race, name='undervote')
            OverUnderCandidates.__overvote_c = Candidate.objects.get(race=race, name='overvote')
        # Store instance reference as the only member in the handle
        self.__dict__['_OverUnderCandidates__instance'] = OverUnderCandidates.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

 

class RankedBallot(models.Model):
    choice_one = models.ForeignKey('rankedvotes.Candidate', blank=True, null=True, related_name='rankedballot_choiceone')
    choice_two = models.ForeignKey('rankedvotes.Candidate', blank=True, null=True, related_name='rankedballot_choicetwo')
    choice_three = models.ForeignKey('rankedvotes.Candidate', blank=True, null=True, related_name='rankedballot_choicethree')
    file_id = models.IntegerField(blank=True, null=True)#unique id from file
    precinct = models.IntegerField(blank=True, null=True)#unique id from file
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    #used when populating objects to save some lookup time
    race = models.ForeignKey('rankedvotes.Race', blank=False, null=False, related_name='rankeballot_race_id')
    #to set the precinct I need the masterfile key to the precinct which I'm not ready to parse so I will save the key here
    precinct_master_lookup = models.CharField(max_length=7, blank=True, null=True)#unique id from file
    precinct_str = models.CharField(max_length=255, blank=True, null=True)#unique id from file
    was_exhausted = models.BooleanField(default=False)

    choices = {}

    def __init__(self, *args, **kwargs):
        super(RankedBallot, self,).__init__(*args, **kwargs)
        #my_choices = self.choices[self.id]


    def get_slate(self):
        return '%s,%s,%s' % (self.choice_one, self.choice_two, self.choice_three)

    def __str__(self):
        return 'c1=%s c2=%s c3=%s' % (self.choice_one, self.choice_two, self.choice_three)

    def __hash__(self):
        #override for insertion into sets
        return self.file_id

    def set_analysis_choices(self):
        overvote_c = OverUnderCandidates(self.race)._OverUnderCandidates__overvote_c
        undervote_c = OverUnderCandidates(self.race)._OverUnderCandidates__undervote_c
        #set queue for analysis
        #invalid ballot
        if self.choice_one == overvote_c or\
         self.choice_two == overvote_c or\
         self.choice_three == overvote_c:
            return []
        #invalid ballot
        elif self.choice_one == undervote_c and\
         self.choice_two == undervote_c and\
         self.choice_three == undervote_c:
            #turn off the ballot and move on
            return []
        elif self.choice_one == undervote_c or\
         self.choice_two == undervote_c or\
         self.choice_three == undervote_c:
            #bump any second or third choices up if 1/2 == undervote
            choices = [self.choice_one.name, self.choice_two.name, self.choice_three.name]
            new_choices = list()
            for i, choice in enumerate(choices):
                if choice != undervote_c.name:
                    new_choices.append(choice)
            return new_choices
        else:
            return [self.choice_one.name, self.choice_two.name, self.choice_three.name]

    def has_blank_choices(self):
        overvote_c = OverUnderCandidates(self.race)._OverUnderCandidates__overvote_c
        undervote_c = OverUnderCandidates(self.race)._OverUnderCandidates__undervote_c
        choices = [self.choice_one.name, self.choice_two.name, self.choice_three.name]
        if overvote_c.name in choices:
            return False
        if undervote_c.name in choices:
            return True

    def unique_choices_cnt(self):
        choices = self.set_analysis_choices()
        return len(Set(choices))

    def has_duplicate_choices(self):
        #look for duplicate choices of a real candidate
        my_choices = self.set_analysis_choices()
        if len(my_choices) != len(Set(my_choices)):
            return True
        else:
            return False

    def get_next_choice(self):
        """
        return a tuple, candidate object and rank order
        """
        overvote_c = OverUnderCandidates(self.race)._OverUnderCandidates__overvote_c
        undervote_c = OverUnderCandidates(self.race)._OverUnderCandidates__undervote_c
        try:
            my_choices = self.choices[self.id]
        except KeyError:
            my_choices = deque([self.choice_one, self.choice_two, self.choice_three])
            self.choices[self.id] = my_choices

        if len(my_choices) > 0:
            if len(my_choices) == 3:
                #SF specific rules
                #we raise undervote exception when we start and all elements are overvote candidates
                if self.choice_one == undervote_c and\
                 self.choice_two == undervote_c and\
                 self.choice_three == undervote_c:
                    #turn off the ballot and move on
                    self.choices[self.id] = deque([])
                    raise UnderVoteException()
                elif self.choice_one == None and self.choice_two == None and\
                 self.choice_three == None:#preserve prior functionality
                    raise ExhaustedBallotException()
                elif self.choice_one == undervote_c:
                    #bump any second or third choices up if 1/2 == undervote
                    if self.choice_two != undervote_c:
                        self.choices[self.id] = deque([self.choice_two, self.choice_three])
                    else:
                        self.choices[self.id] = deque([self.choice_three])
                    my_choices = self.choices[self.id]
                        
            candidate = my_choices.popleft()
            if candidate == undervote_c:
                raise UnderVoteException()
            elif candidate == overvote_c:
                raise OverVoteException()
            elif candidate == None:
                raise ExhaustedBallotException()
            else:
                return (candidate, len(my_choices)%3)
        else:
            raise ExhaustedBallotException()
