from sys import argv

from django.db.models import Q

from datetime import datetime
from rankedvotes.models import Race, Candidate, RankedBallot 
from rankedchoice.models import RankedChoiceRound, CandidateRoundRank
from rankedvotes.models import ExhaustedBallotException, OverVoteException, UnderVoteException

"""
sf rules
Undervotes can occupy all ballot choices these ballots are exhausted in 0 round
Ballots are made exhausted when the first overvote occurs (round 0 or more)
If an undercount occurs in either position 1 or 2, the next position is used for that choice.  If a ballot is undercounted for the third choice is becomes exhausted
"""

# This can now be run straight from the console
# ./manage.py runscript rankedchoice.scripts.calculate_rcv 'Science of Voting'


#store candidate ranking objs 
candidate_rankings = {}

def run():
    race_name=argv[3]
    #http://www.acgov.org/rov/rcv/results/rcvresults_2984.htm
    #this contest
    race = Race.objects.get(name=race_name)

    # Delete existing Ranked Choice Rounds for Race
    RankedChoiceRound.objects.filter(race=race).delete()

    # Delete Candidate Round Ranks and associated Round of Votes
    candidate_rounds = CandidateRoundRank.objects.filter(race=race)
    for crr in candidate_rounds:
        crr.roundovotes.all().delete() 
    candidate_rounds.delete()

    #TODO should be a function of race
    all_candidates = Candidate.objects.filter(race=race).exclude(Q(name='overvote')|Q(name='undervote'))
    all_ballots = race.get_ballots_to_process()

    total_ballots_cnt = race.get_ballots_cnt()

    exhausted_ballots = list()
    overvotes = 0
    undervotes = 0

    #do we keep iterating?
    next_round = True
    #current round
    round = 1
    #store prior rounds in memory so we don't have to retrieve the objs and clear data structures
    rounds = {}
    print 'status, round, candidate, total_votes, 1st, 2nd, 3rd, eb, undervotes, overvotes'

    while next_round:
        avail_cand_list = None
        if round == 1:
            #the world is our oyster
            avail_cand_list = all_candidates
            ballots = all_ballots
            dropped_candidates = []
        else:
            #get prior round
            last_round = rounds[round-1]
            #list of the candidate_ranking objects containing candidates we shouldn't use
            dropped_candidates = eleminate_candidates(last_round)

            #check to see if the number o dropped candidates = number o avail candidats
            #means we have a tie between two or more candidates
            if len(last_round.candidate_rankings.all()) == len(dropped_candidates):
                print 'we have a tie between candidates'
                break

            #use only the avail candidates..
            avail_candidates = filter((lambda x: x not in dropped_candidates), 
                last_round.candidate_rankings.all())
            #make a list of candidates for comparison
            avail_cand_list = map((lambda x: x.candidate), avail_candidates)

            ballots = list()
            #reclaim ballots
            for c in dropped_candidates:
                new_ballots = c.get_ballots()
                for b in new_ballots:
                    ballots.append(b)

        #lists for each ranking w/ that will contain tuple of candidate + ballot
        choice_ones = list()
        choice_twos = list()
        choice_threes = list()
        #begin distribution process
        for i, ballot in enumerate(ballots):
            found_candidate = False
            while not found_candidate:
                try:
                    choice_rank = ballot.get_next_choice()
                    if choice_rank[0] not in avail_cand_list:
                        #hack to take care of not checking to see if the next candidate
                        #is still in avail_list... max 2 choices are left
                        #at this point so do it 2x
                        choice_rank = ballot.get_next_choice()
                        if choice_rank[0] not in avail_cand_list:
                            choice_rank = ballot.get_next_choice()
                    candidate = choice_rank[0]
                    ranking = choice_rank[1]
                    if ranking == 2:
                        choice_ones.append((candidate, ballot))
                    if choice_rank[1] == 1:
                        choice_twos.append((candidate, ballot))
                    elif choice_rank[1] == 0:
                        choice_threes.append((candidate, ballot))
                    found_candidate = True
                except UnderVoteException:
                    if round == 1:
                        #sf rule, we only count undervotes in the 0th round
                        undervotes += 1
                        #first round undervotes are actually exhausted ballots
                        #but we need to keep track of em so heres a bit of hack
                        found_candidate = True
                except OverVoteException:
                    overvotes += 1
                    #TODO: SF Specific rule, subclass me to do this for specific muni
                    #first overvote makes ballot invalid
                    #overvotes are technically exhausted_ballots but we can't
                    #them as part of the same pile cus oakland don't
                    #exhausted_ballots.append(ballot)
                    found_candidate = True
                except ExhaustedBallotException:
                    ballot.was_exhausted = True
                    ballot.save()
                    exhausted_ballots.append(ballot)
                    #didn't find a candidate, technically, but we gotta break now
                    found_candidate = True

        #we got the temporary results, go ahead and mark ballots used by choice
        votes_to_distribute = redistribute_votes(choice_ones, avail_cand_list)
        #update candidates new choice2 votes, 0idx rank 
        update_candidate_votes_for_round(votes_to_distribute, 0, race, round)

        #we got the temporary results, go ahead and mark ballots used by choice
        votes_to_distribute = redistribute_votes(choice_twos, avail_cand_list)
        #update candidates new choice2 votes, 0idx rank 
        update_candidate_votes_for_round(votes_to_distribute, 1, race, round)
        
        #we got the temporary results, go ahead and mark ballots used by choice
        votes_to_distribute = redistribute_votes(choice_threes, avail_cand_list)
        #update candidates new choice2 votes, 0idx rank 
        update_candidate_votes_for_round(votes_to_distribute, 2, race, round)

        #avail_candidates = CandidateRoundRank.objects.filter(race=race, round=round)

        cont_ballots = total_ballots_cnt - undervotes - overvotes - (len(exhausted_ballots))
        #serialize this round
        this_round = RankedChoiceRound(round=round, race=race, 
            exhausted_ballots=len(exhausted_ballots), undervoted_ballots=undervotes,
            overvoted_ballots=overvotes, continuing_ballots=cont_ballots)
        rounds[round] = this_round
        this_round.save()

        #TODO rm when RankedChoiceRound becomes RoundManager
        if round == 1:
            avail_candidates = map((lambda x:candidate_rankings[x]), candidate_rankings.keys())

        this_round.candidate_rankings = avail_candidates
        this_round.dropped_candidates = dropped_candidates

        print 'ROUND %s SUMMARY: total_ballots=%s continuing_ballots=%s exhausted_ballots=%s overvotes=%s undervotes=%s' % (
            round,
            total_ballots_cnt,
            cont_ballots,
            len(exhausted_ballots),
            overvotes,
            undervotes)

        #update the console
        for candidate_round_rank in avail_candidates:
            round_results = candidate_round_rank.get_results_up_to_round(round)
            print 'IN CANDIDATE,%s,%s,%s,%s,%s,%s,%s' % (round,
                candidate_round_rank.candidate,
                candidate_round_rank.get_total_votes(),
                round_results[0], round_results[1],
                round_results[2], round_results[3])


        for candidate_round_rank in this_round.dropped_candidates.all():
            round_results = candidate_round_rank.get_results_up_to_round(round)

            print 'DROPPED CANDIDATE,%s,%s,%s,%s,%s,%s,%s' % (round,
                candidate_round_rank.candidate,
                candidate_round_rank.get_total_votes(),
                round_results[0], round_results[1],
                round_results[2], round_results[3])

        #all votes
        total_votes = this_round.get_vote_universe()
        #threshold for a winner
        winning_threshold = (total_votes / 2) + 1

        results = sort_contest(this_round.candidate_rankings.all())
        #stop executing or eleminate candidates
        if len(results) != 0 and results[0].get_total_votes() >= winning_threshold or len(results) == 1:
            print 'winner=%s votes=%s exhausted_ballots=%s overvotes=%s undervotes=%s' % (
                results[0].candidate, 
                results[0].get_total_votes(), 
                len(exhausted_ballots)-overvotes,
                overvotes,
                undervotes)
            next_round = False
        elif len(results) == 0:
            next_round = False
            print 'no one won, did all the candidates get eliminated in the last round?'

        #next round
        round += 1

def update_candidate_votes_for_round(votes_to_distribute, rank, race, round):
    """
    votes_to_distribute: dict of candidate names to the ballots they need
    """
    for key in votes_to_distribute.keys():
        if round == 1:
            candidate_rr, created = CandidateRoundRank.objects.get_or_create(candidate=key, race=race, round=round) 
        else:#i want to get rid of this logic but I can't until refactoring of the RankedChoiceRound occurs
            candidate_rr = candidate_rankings[key]
        candidate_rr.round = round
        candidate_rr.add_votes_to_round(round, rank, votes_to_distribute[key])
        candidate_rr.save()
        candidate_rankings[key] = candidate_rr
    

def redistribute_votes(votes, available_candidates):
    """
    votes: list of tuples containing candidate objects  and the ballot he came from
    available_candidates: list of candidates still in the race

    return: a dict o'candidates where each candidate has a list of ballots belonging to him
    """
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

def eleminate_candidates(this_round):
    """
    Return a list of CandidateRoundRank objects
    for candidates who didn't make the cut
    """
    results = sort_contest(this_round.candidate_rankings.all())
    if len(results) <= 1:
        return [] #no candidates left to drop
    #drop candidate with least # of votes
    dropped_candidates = list()
    dropped_candidates.append(results[len(results)-1])
    del results[len(results)-1]
    #double check for other candidates with lowest # of votes
    #SF Rules, if to total dropped votes + next candidates 
    total_dropped_votes = dropped_candidates[0].get_total_votes() #is this total dropped votes for this ROUND or the whole RACE?
    for idx in reversed(xrange(0, len(results))):
        this_candidate_votes = results[idx].get_total_votes()
        d_candidate_votes = dropped_candidates[0].get_total_votes()
        if this_candidate_votes == d_candidate_votes:
            dropped_candidates.append(results[idx])
        """
        if idx == 0:
            break 
        next_candidate = results[idx-1]

        print 'this_candidate=%s votes=%s next_candidate=%s votes=%s total_dropped_votes=%s dropped+this=%s' %\
         (results[idx].candidate, results[idx].get_total_votes(), next_candidate, next_candidate.get_total_votes(),\
         total_dropped_votes, total_dropped_votes + this_candidate_votes)

        if (this_candidate_votes + total_dropped_votes) < next_candidate.get_total_votes():
            dropped_candidates.append(results[idx])
            total_dropped_votes += this_candidate_votes
        else:
            break #we can break now
        """
    
    return dropped_candidates

def sort_contest(candidate_rankings):
    #sort to get some answers
    return sorted(candidate_rankings,
        key=lambda candidate_rr: candidate_rr.get_total_votes(), reverse=True)
