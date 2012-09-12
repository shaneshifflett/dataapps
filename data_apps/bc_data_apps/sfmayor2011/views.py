import logging

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Count, Sum, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect, Http404 
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from contact_form.views import contact_form
from content.models import Content 
from locations.models import Coordinates
from emails.mailer import *
from generics.utils import paginate_list

from sfmayor2011.forms import ContributionsSearchForm, AskACandidateForm, ReportElectionProblemsForm
from sfmayor2011.models import *
from sfmayor2011.tables import *

@receiver(post_save, sender=AskACandidate)
def saved_question_handler(sender, **kwargs):
    """
    notify staff of a question once it has been asked
    """
    try:
        context = {}
        obj = kwargs['instance']
        context['name'] = obj.name
        context['candidate'] = obj.get_candidate_name
        context['phone'] = obj.phone
        context['question'] = obj.description
        context['email'] = obj.email
        send_multipart_mail(template_name="new_question", email_context=context,\
            recipients=['dev@baycitizen.org', 'askacandidate@baycitizen.org'], appname=obj._meta.app_label,\
            sender='Bay Citizen Tech Team <dev@baycitizen.org>')
    except Exception as e:
        logging.error("sfmayor2011.saved_question_handler: error sending email e=" % e)

def get_content(request, template_name='sfmayor2011/sfmayor_content_items.html'):
    context = {}
    content = (Content.published_objects.filter(primary_topic__slug='sf-mayoral-race',
        publication_status='P').order_by('-pub_date').exclude(
            Q(classname='videos.video') | Q(classname='images.image') | 
            Q(classname='images.gallery')))[5:]
    pages, current_page = paginate_list(request, content)
    context['pages'] = pages
    context['current_page'] = current_page
    context['content'] = current_page.object_list
    context['cssname'] = 'stories-Story'
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def get_content_candidates(request, slug, template_name='sfmayor2011/sfmayor_content_items.html'):
    try:
        context = {}
        candidate = get_object_or_404(Candidate, entity__full_name__slug=slug)
        related_content = Content.objects.filter((Q(content_type__name='story')|\
         Q(content_type__name='post')), body__contains=candidate.entity.full_name.name,\
          publication_status='P').order_by('-pub_date')
        pages, current_page = paginate_list(request, related_content)
        context['pages'] = pages
        context['current_page'] = current_page
        context['content'] = current_page.object_list
        context['cssname'] = 'stories-Story'
    except Exception as e:
        print e
        logger.error('sfmayor2011.get_content_candidates e=%s' % e) 
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def sfmayor_topic_redirect(request, topic=None):
    return HttpResponseRedirect(reverse('sfmayor_index'))

def index(request, template_name='sfmayor2011/sfmayor_index.html'):
    context = {}
    context['candidates'] = Candidate.objects.all().exclude(Q(bio='')|Q(bio=None)|Q(bio='test bio zzzz')).order_by('entity__full_name__name')
    context['stories'] = (Content.published_objects.filter(
        primary_topic__slug='sf-mayoral-race', 
        publication_status='P').order_by('-pub_date').exclude(
            Q(classname='videos.video') | Q(classname='images.image') | 
            Q(classname='images.gallery')))[0:5]
    content = (Content.published_objects.filter(
        primary_topic__slug='sf-mayoral-race', 
        publication_status='P').order_by('-pub_date').exclude(
            Q(classname='videos.video') | Q(classname='images.image') | 
            Q(classname='images.gallery')))[5:]
    pages, current_page = paginate_list(request, content)
    context['pages'] = pages
    context['current_page'] = current_page
    context['content'] = current_page.object_list
    context['cssname'] = 'stories-Story'
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def ask_candidate(request, template_name='sfmayor2011/sfmayor_candidate_question.html'):
    context = {}
    if request.method == 'GET':
        context['form'] = AskACandidateForm()
    else:
        form = AskACandidateForm(request.POST)
        if form.is_valid():
            obj = form.save()
            template_name='sfmayor2011/sfmayor_question_thanks.html'
        else:
            context['form'] = form
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def list_candidates(request, template_name='sfmayor2011/sfmayor_candidate_listing.html'):
    context = {}
    context['candidates'] = Candidate.objects.all().exclude(Q(bio='')|Q(bio=None)|Q(bio='test bio zzzz'))
    context['num_candidates'] = len(context['candidates'])
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def candidate(request, slug, template_name='sfmayor2011/sfmayor_candidate.html'):
    context = {}
    candidate = get_object_or_404(Candidate, entity__full_name__slug=slug)
    candidates = get_candidates_w_bios()
    if candidate not in candidates:
        raise Http404
    context['candidate'] = candidate
    context['candidates'] = candidates
    #want to be a little looser with the stories displayed on candidate pages
    #so there is some content
    related_content = Content.objects.filter((Q(content_type__name='story')|\
     Q(content_type__name='post')), body__contains=candidate.entity.full_name.name,\
      publication_status='P').order_by('-pub_date')
    pages, current_page = paginate_list(request, related_content)
    context['pages'] = pages
    context['current_page'] = current_page
    context['content'] = current_page.object_list
    context['cssname'] = 'stories-Story'
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def faq(request, template_name='sfmayor2011/sfmayor_faq.html'):
    context = {}
    context['candidates'] = Candidate.objects.all()
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def poll_locations(request, template_name='sfmayor2011/sfmayor_poll_locations.html'):
    context = {}
    context['candidates'] = Candidate.objects.all()
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def polls(request, template_name='sfmayor2011/sfmayor_polls.html'):
    context = {}
    context['candidates'] = Candidate.objects.all()
    context['rankings'] = []
    context['polls'] = Poll.objects.all().order_by('-date')
    for c in Candidate.objects.all():
        rankings = PollRanking.objects.filter(candidate=c).order_by('-poll__date')
        if len(rankings) > 0:
            context['rankings'].append((c.get_name(), rankings, rankings[0].poll.source.full_name.name))
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def contributions(request, template_name='sfmayor2011/sfmayor_contributions.html'):
    context = {}
    candidates = (Candidate.objects.all())
    context['candidates'] = candidates
    #context['contribs'] = sorted_contributions(candidates)
    contributions = sorted(candidates, key=lambda candidate: candidate.public_financing+candidate.other_financing, reverse=True)
    context['contribs'] = contributions
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def contributions_list(request, slug=None, template_name='sfmayor2011/sfmayor_contributions_list.html'):
    context = {}
    context['candidates'] = Candidate.objects.all()
    query = Contribution.objects.all()
    form = ContributionsSearchForm()
    dollar_amt = Contribution.objects.all().aggregate(Sum('amount'))
    context['name'] = 'all candidates'
    if request.method == 'GET':
        form = ContributionsSearchForm(request.GET)
        if form.is_valid():
            kwargs = {}
            candidate = form.cleaned_data.get('candidate_name', None)
            if candidate == '' and slug != None:
                candidate_o = get_object_or_404(Candidate, entity__full_name__slug=slug)
                candidate = candidate_o.entity.full_name.name
                context['name'] = candidate_o.entity.full_name.name
            elif candidate != '':
                context['name'] = candidate
            contributor = form.cleaned_data.get('contributor_name', None)
            occupation = form.cleaned_data.get('occupation', None)
            date_to = form.cleaned_data.get('date_to', None)
            date_from = form.cleaned_data.get('date_from', None)
            amount = form.cleaned_data.get('amount', None)
            employer = form.cleaned_data.get('employer', None)
            city = form.cleaned_data.get('city', None)
            state = form.cleaned_data.get('state', None)
            if candidate:
                kwargs['candidate__entity__full_name__name__icontains'] = candidate
            if contributor:
                kwargs['contributor__full_name__name__icontains'] = contributor
            if occupation:
                kwargs['occupation__name__icontains'] = occupation
            if date_from:
                kwargs['date__gte'] = date_from
            if date_to:
                kwargs['date__lte'] = date_to
            if amount:
                kwargs['amount'] = amount
            if employer:
                kwargs['employer__name__icontains'] = employer
            if city:
                kwargs['place__city__icontains'] = city
            if state:
                kwargs['place__state__icontains'] = state
            query = Contribution.objects.filter(**kwargs)
            dollar_amt = Contribution.objects.filter(**kwargs).aggregate(Sum('amount'))
    table = ContributionTable(query, order_by=request.GET.get('sort', '-date'))
    page = request.GET.get('page')
    if page == None or page == '':
        page = 1
    context['results_cnt'] = table.rows.count()
    if dollar_amt['amount__sum'] == None:
        context['dollar_amt'] = 0.00
    else:
        context['dollar_amt'] = dollar_amt['amount__sum'].to_eng_string()
    table.paginate(Paginator, 50, page=page, orphans=10)
    context['table'] = table
    context['form'] = form
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def contributions_map(request, template_name='sfmayor2011/sfmayor_contribs_map.html'):
    context = {}
    cities = Contribution.objects.all().exclude(place__city='San Francisco').values_list('place__city',\
     'place__state', 'place__coordinates').distinct()
    vals = list()
    for c in cities:
        city = c[0]
        state = c[1]
        amt = Contribution.objects.filter(place__city=city,\
         place__state=state).aggregate(Count('amount'))
        if amt != None and c[2] != None:
            coords = Coordinates.objects.get(id=c[2])
            dollar_amt = amt['amount__count']
            vals.append((city+', '+state, dollar_amt, coords.latitude, coords.longitude))
    context['vals'] = vals
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def report_election_problems(request, template_name='sfmayor2011/sfmayor2011_report_election_problems.html'):
    success_url = reverse('sfmayor2011_report_election_problems_sent')
    return contact_form(request, form_class=ReportElectionProblemsForm, template_name=template_name, success_url=success_url)
