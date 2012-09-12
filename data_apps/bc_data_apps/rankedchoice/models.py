from django.db import models

class RoundOVotes(models.Model):
    """
    total votes received for a round, for a candidate
    """
    votes = models.IntegerField(default=0)
    round = models.IntegerField(default=0)
    #-1 = exhausted ballot count, 0=1st choice, 1=2nd choice, 2=3rd choice
    rank_order = models.IntegerField(default=0)

    def __str__(self):
        return "%d votes in round %d rank %d"%(self.votes, self.round, self.rank_order+1)

    def __unicode__(self):
        return u'%s'%(self.__str__())


class CandidateRoundRank(models.Model):
    candidate = models.ForeignKey('rankedvotes.Candidate', blank=False, null=False)
    roundovotes = models.ManyToManyField('rankedchoice.RoundOVotes',\
     symmetrical=False, null=True, blank=True)
    race = models.ForeignKey('rankedvotes.Race', blank=False, null=False, related_name='crr_race')
    round = models.IntegerField()
    #I need a unique set of ballot references so when I'm removed from a round
    #I can transfer my ballots to a new candidate
    #I will initially contain all first choice ballots 
    #eventually, I will contain other candidates second and third choice ballots
    ballots_used = {}
    

    def __init__(self, *args, **kwargs):
        super(CandidateRoundRank, self,).__init__(*args, **kwargs)

    def __str__(self):
        return "%s's votes in %s"%(self.candidate.name, self.race.name )

    def __unicode__(self):
        return u'%s'%(self.__str__())

    def add_ballots(self, ballots):
        for b in ballots:
            if self.id in self.ballots_used.keys():
                self.ballots_used[self.id].append(b)
            else:        
                self.ballots_used[self.id] = [b]

    def get_ballots(self):
        if self.id in self.ballots_used.keys():
            return self.ballots_used[self.id]
        else:
            return []
        
    def get_total_votes(self):
        try:
            return self._total_votes
        except:
            total = 0
            for round in self.roundovotes.all().exclude(rank_order=-1):
                total += round.votes
            self._total_votes = total
            return self._total_votes


    def get_total_votes_up_to_round(self, round):
        total = 0
        for round in self.roundovotes.filter(round__lte=round).exclude(rank_order=-1):
            total += round.votes
        return total

    def get_round_results(self, round):
        """
        return a list of votes
        element 0: choice one votes for this round
        element 1: choice two votes for this round
        element 2: choice three votes for this round
        element 3: number of exhausted ballots
        """
        round_n_ranks = self.roundovotes.filter(round=round).exclude(rank_order=-1)
        results = [0,0,0,0]
        total = 0
        for rnr in round_n_ranks:
            results[rnr.rank_order] = rnr.votes
            total += rnr.votes
        eb = self.roundovotes.filter(round=round).exclude(rank_order__gte=0)
        for e in eb:
            results[3] += e.votes
        return results

    def get_results_up_to_round(self, round):
        """
        return a list of votes accounting for prior rounds up to this round
        element 0: choice one votes for this round
        element 1: choice two votes for this round
        element 2: choice three votes for this round
        element 3: number of exhausted ballots
        """
        round_n_ranks = self.roundovotes.filter(round__lte=round).exclude(rank_order=-1)
        results = [0,0,0,0]
        total = 0
        for rnr in round_n_ranks:
            results[rnr.rank_order] += rnr.votes
            total += rnr.votes
        eb = self.roundovotes.filter(round__lte=round).exclude(rank_order__gte=0)
        for e in eb:
            results[3] += e.votes
        return results

    def add_votes_to_round(self, round, rank, votes):
        round, created = self.roundovotes.get_or_create(round=round, rank_order=rank)
        round.votes += len(votes)
        self.add_ballots(votes)
        round.save()

    def add_exhausted_ballots(self, round, votes):
        round, created = self.roundovotes.get_or_create(round=round, rank_order=-1)
        round.votes += len(votes)
        round.save()
        self.roundovotes.add(round)

class RankedChoiceRound(models.Model):
    """
    This class should become RoundManager and be able to 
    retrieve the votes for each candidate for each round with ease
    return complete results for each round
    give granular data points for each round including
    #of undervotes, overvotes, exhuasteds, etc
    """
    candidate_rankings = models.ManyToManyField('rankedchoice.CandidateRoundRank',\
     symmetrical=False, null=True, blank=True)
    round = models.IntegerField()
    race = models.ForeignKey('rankedvotes.Race', blank=False, null=False)
    exhausted_ballots = models.IntegerField()
    overvoted_ballots = models.IntegerField()
    undervoted_ballots = models.IntegerField()
    continuing_ballots = models.IntegerField()
    dropped_candidates = models.ManyToManyField('rankedchoice.CandidateRoundRank', blank=True, null=True,
     symmetrical=False, related_name='rankedchoiceround_dropped_candidates')
    text = models.TextField(null=True, blank=True)

    """
    TODO: refactor and implement: logic to track current counds for a round, give information about prior rounds
    lives here
    For logic to work during RCV calc, only one instance of a RoundManager can exist per race
    Each candidate will have one instace of a CandidateRoundRank that will keep track of his ballots during RCV runtime
    RoundManager will keep track of all candidate_rankings that exist for this race
    _candidate_ranking_mem_objs = None

    if i do that now it'll break teh views
    def redistribute_votes(self, votes, available_candidates):
        #figure out which candidates get new votes second choice
        c_dict = {}
        for c in votes:
            candidate = c[0]
            #gotta check every vote to see if the candidate is still in
            if candidate != None and candidate in available_candidates:
                if candidate in c_dict.keys():
                    c_dict[candidate].append(c[1])
                else:
                    c_dict[candidate] = [c[1]]
            else:
                #otherwise, no candidate was selected for this choice 
                pass #TODO if a candidate wasn't marked do I throw under/over vote error here?

        return c_dict

    def update_candidate_rankings(self, votes_to_distribute, rank, round):
        for key in votes_to_distribute.keys():
            if round == 1:
                candidate_rr, created = CandidateRoundRank.objects.get_or_create(candidate=key, race=self.race, round=round)
                candidate_rr.save()
                self._candidate_ranking_mem_objs[candidate_rr.candidate] = candidate_rr
                print 'round=%s candidate=%s' % (round, candidate_rr)
            candidate_rr = self._candidate_ranking_mem_objs[key]
            candidate_rr.round = round
            candidate_rr.add_votes_to_round(round, rank, votes_to_distribute[key])
            candidate_rr.save()
        self.candidate_rankings = self.get_candidate_rankings()    
        print self._candidate_ranking_mem_objs


    def get_candidate_rankings(self, round):
        return filter((lambda x:self._candidate_ranking_mem_objs[x].round == round), self._candidate_ranking_mem_objs.keys())

    def get_candidate_rankings(self):
        #allow this RoundManager to keep track of all candidate rankings
        #in memory so we can transfer ballots appropriately
        if self._candidate_ranking_mem_objs == None:
            self._candidate_ranking_mem_objs = {}
            return []
        #return a list of candidate rankings
        return map((lambda x:self._candidate_ranking_mem_objs[x]), self._candidate_ranking_mem_objs.keys())

    """


    def __str__(self):
        return '%s round %d' %(self.race.name, self.round)

    def __unicode__(self):
        return u'%s'%(self.__str__())

    def get_discarded_ballot_cnt(self):
        try:
            return self._discarded_ballot_cnt
        except:
            self._discarded_ballot_cnt = self.exhausted_ballots + self.undervoted_ballots + self.overvoted_ballots
            return self._discarded_ballot_cnt

    def set_candidate_rankings(self):
        rankings = CandidateRoundRank.objects.filter(race=self.race, round=self.round)
        self.candidate_rankings = rankings

    def print_outcome(self):
        print 'Candidate, total_votes, round_votes, Round'
        for c in self.candidate_rankings.all():
            roundovotes = c.get_round_results(self.round)
            print '%s,%s,%s,%s'\
             % (c.candidate.name, c.get_total_votes(), roundovotes.votes, self.round)

    def get_vote_universe(self):
        total = 0
        for crr in self.candidate_rankings.all():
            total += crr.get_total_votes()
        return total
       
    def get_avail_vote_universe(self):
        total = 0
        for crr in self.candidate_rankings.all():
            these = crr.get_results_up_to_round(self.round)
            total += these[0]+these[1]+these[2]
        return total
