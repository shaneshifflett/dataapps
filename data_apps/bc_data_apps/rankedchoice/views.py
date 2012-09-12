from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect

from data_apps.bc_data_apps.rankedchoice.models import RankedChoiceRound
from data_apps.bc_data_apps.rankedvotes.models import Race

from django.contrib.humanize.templatetags.humanize import intcomma


def index(request, template_name="rankedchoice/rankedchoice_index.html"):
    #context = {}
    #context['page_title'] = 'Ranked Choice Voting'
    #return render_to_response(template_name, context, context_instance=RequestContext(request))
    return HttpResponseRedirect('/data/rankedchoice/bay-citizen-usf-mayoral-poll/')

def race(request, slug, template_name="rankedchoice/rankedchoice_race.html"):
    context = {}
    race=get_object_or_404(Race,slug=slug)
    context['num_rounds'] = RankedChoiceRound.objects.filter(race=race).count() 
    context['race'] = race
    context['page_title'] = 'Ranked Choice Voting'
    final_round=RankedChoiceRound.objects.get(race=race, round=context['num_rounds'])
    max_votes=0
    discarded_ballots = final_round.get_discarded_ballot_cnt()
    for ccr in final_round.candidate_rankings.all():
        total = sum( ccr.get_results_up_to_round(context['num_rounds']))
        if total>max_votes:
            max_votes = total 

    if discarded_ballots > max_votes:
        max_votes = discarded_ballots
    context['graph_scale'] = max_votes
    context['slug'] = slug

    context['total_votes'] = intcomma(race.get_ballots_cnt())


    context['cssname'] = 'stories-Story'
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def text(request, slug, round_num):
    race = Race.objects.filter(slug=slug)
    rc_round = RankedChoiceRound.objects.get(race=race, round=round_num)
    response = rc_round.text or ''
    
    try: 
        rc_round_next = RankedChoiceRound.objects.get(race=race, round=int(round_num)+1)

        bottom_crr = rc_round.candidate_rankings.all()[0]
        for crr in rc_round.candidate_rankings.all():
            if crr.get_total_votes() < bottom_crr.get_total_votes():
                bottom_crr = crr
       
        dropped_candidates = []
        for crr in rc_round.candidate_rankings.all():
            if crr.get_total_votes() == bottom_crr.get_total_votes():
                 dropped_candidates.append(crr.candidate.name) 

        distribution = []
        for next_crr in rc_round_next.candidate_rankings.all():
            vote_diff = sum(next_crr.get_round_results(rc_round_next.round))
            if vote_diff > 0:
                if vote_diff > 1:
                    vote_str = 'votes'
                else:
                    vote_str = 'vote'
                distribution.append("%s %s to %s" % (intcomma(vote_diff), vote_str, next_crr.candidate.name))

        dropped_candidates_text = ', '.join(dropped_candidates) 
        response = response + 'No candidate has a majority.  %s has the fewest votes, and will be eliminated. <br/>That gives %s' % (dropped_candidates_text, ', '.join(distribution))
    except Exception as e:
        print 'e=%s' %e

    return HttpResponse(response)

def format_name(name):
    lim = 14
    if len(name) > lim:
        ret_val = name[0:lim] + "..."
    else:
        ret_val = name
    return ret_val

def step(request, slug, round_num):
    result=[]
    available_candidates = []
    dropped_candidates = []
    race = Race.objects.get(slug=slug)
    try:
   
        rc_round=RankedChoiceRound.objects.get(race=race,round=round_num)
        top_crr = rc_round.candidate_rankings.all()[0] 
        for crr in rc_round.candidate_rankings.all().order_by('candidate__name'): 
            c_name = format_name(crr.candidate.name)
            available_candidates.append(c_name)
            result.append({'label':c_name,
                           'values': crr.get_results_up_to_round(round=round_num)})
            if crr.get_total_votes() > top_crr.get_total_votes(): 
                top_crr = crr

        #get all dropped candidates
        rounds = RankedChoiceRound.objects.filter(race=race,round__lte=round_num)
        for r in rounds:
            for crr in r.dropped_candidates.all():
                c_name = format_name(crr.candidate.name)
                dropped_candidates.append(c_name)
                result.append({'label': c_name,
                               'values': [0,0,0,0]})


        round_dict={}
        if(int(round_num)==1):
            round_dict['label'] = ('First Choice Votes', 'Second Choice Votes', 'Third Choice Votes', 'Exhausted Ballots' )
        result.append({'label':'Discarded Ballots',
                       'values':[0,0,0,int(rc_round.exhausted_ballots) + rc_round.overvoted_ballots + rc_round.undervoted_ballots]})

        round_dict['values'] = result
        round_dict['color'] = ['#5ebd59', '#d6d434', '#d69734', '#bd5959']
        round_dict['top_candidate'] = top_crr.candidate.name 
        top_candidate_total_votes = top_crr.get_total_votes()
        total_valid_ballots = rc_round.continuing_ballots
        round_dict['total_valid_ballots'] = intcomma(total_valid_ballots)
        round_dict['top_candidate_percentage'] = '%2.2f' % ((float(top_candidate_total_votes) / total_valid_ballots) * 100)
        round_dict['available_candidates'] = available_candidates
        round_dict['dropped_candidates'] = dropped_candidates
        round_dict['remaining_votes'] = intcomma(total_valid_ballots)
        round_dict['total_votes'] = intcomma(race.get_ballots_cnt())
        round_dict['undervotes'] = intcomma(rc_round.undervoted_ballots)
        round_dict['overvotes'] = intcomma(rc_round.overvoted_ballots)
        round_dict['exhausted_ballots'] = intcomma(rc_round.exhausted_ballots)
    except Exception as e:
        print 'e=%s' %e

    return HttpResponse(simplejson.dumps(round_dict))
