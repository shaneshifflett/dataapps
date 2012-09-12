import random
import re

from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import never_cache

from twilio import twiml

from rankedvotes.forms import RankedBallotForm
from rankedvotes.models import Race, RankedBallot, Candidate

def voice(request):
    r = twiml.Response()
    r.say('Welcome to The Bay Citizen Cal Academy Science of Voting Event.  Please send an SMS text to this number 4 1 5 4 1 8 7 5 5 1, in order to vote for your top three favorite animals.', voice='woman')
    return HttpResponse(r.toxml())

@never_cache
def text_vote(request):
    account_sid = request.REQUEST.get('AccountSid')
    r = twiml.Response()
    if account_sid == 'ACf2f21afc52cd4b5e9705cf14c94d9de1':
        choices = {
            'g': 'Giraffe',
            'a': 'Alligator',
            'p': 'Penguin',
            'j': 'Jaguar',
            's': 'Spider'
        }
        race = Race.objects.get(id=2)
        phone_number = request.REQUEST.get('From')
        raw_message = request.REQUEST.get('Body') 
        message = raw_message.lower()
        message = message.replace(',','')
        # Remove whitespace
        message = re.sub(r'\s', '', message)
        # Randomly generate sample Message
        sample_message = ''.join(random.sample(choices.keys(), 3))  
        try:
            choice1 = Candidate.objects.get(name=choices[message[0]]) 
            if message[1] != message[0]:
                choice2 = Candidate.objects.get(name=choices[message[1]]) 
            else:
                choice2 = None
            if message[2] != message[1] or message[2] != message[0]:
                choice3 = Candidate.objects.get(name=choices[message[2]])
            else:
                choice3 = None
            ballot = RankedBallot(choice_one=choice1, choice_two=choice2, choice_three=choice3, race=race, phone_number=phone_number)
            ballot.save()
            r.sms("Thanks for submitting your vote of %s(1st choice), %s(2nd), %s(3rd)" % (ballot.choice_one, ballot.choice_two, ballot.choice_three))
        except:
            r.sms("Sorry but your submission of '%s' is not valid.  Please try again and enter 3 out of the 5 valid letters (g,a,p,j,s) for example '%s'.  Thanks!" % (raw_message, sample_message))
    else:
        r.sms("Invalid Input - Requests must be sent from a SMS text")
    return HttpResponse(r.toxml()) 

@never_cache
@staff_member_required
def new_ballot(request, slug, template_name="rankedvotes/rankedvotes_ballot.html"):
    context = {}
    race = get_object_or_404(Race, slug=slug)
    if request.method == 'GET':
        candidates = Candidate.objects.filter(race=race).values_list('slug', 'name')
        options = {'first_choice': candidates, 'second_choice': candidates, 'third_choice':candidates}
        form = RankedBallotForm(initial=options)
        context['race'] = race
        context['form'] = form
        return render_to_response(template_name, context, context_instance=RequestContext(request))
    else:
        first_choice = request.POST['first_choice']
        second_choice = request.POST['second_choice']
        third_choice = request.POST['third_choice']

        f1 = Candidate.objects.get(slug=first_choice, race=race)
        if second_choice != first_choice:
            f2 = Candidate.objects.get(slug=second_choice, race=race)
        else:
            f2 = None
        if third_choice != second_choice or third_choice != first_choice:
            f3 = Candidate.objects.get(slug=third_choice, race=race)
        else:
            f3 = None

        rb = RankedBallot(choice_one=f1, choice_two=f2, choice_three=f3, race=race, file_id=-99)
        rb.save()
        template_name="rankedvotes/rankedvotes_thanks.html"
        #erm for some reason ballot is still empty after save, but the object exists in db
        context['ballot'] = rb
        return HttpResponseRedirect(reverse('rankedvotes_thanks', kwargs={'rbid': rb.id}))

def thanks(request, rbid, template_name="rankedvotes/rankedvotes_thanks.html"):
    context = {}
    context['ballot'] = RankedBallot.objects.get(id=int(rbid))
    return render_to_response(template_name, context, context_instance=RequestContext(request))
