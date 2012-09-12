from sfmayor2011.models import *
from django.template.defaultfilters import slugify
from decimal import Decimal
from datetime import datetime, date
import csv
import re
import string


def sept_filing_aggregate_numbers():

    contribs = {
    'Bevan Dufty':616799.56,
    'David Chiu':546455.49,
    'Dennis Herrera':718722.59,
    'Ed Lee':748007.57,
    'Jeff Adachi':90084,
    'Joanna Rees':416749,
    'John Avalos':158278.98,
    'Leland Yee':586548.78,
    'Michela Alioto-Pier':221879,
    'Phil Ting':149484,
    'Terry Baum':23905,
    'Tony Hall':127602,
    'Wilma Pang':8425,
    }

    public_finance = {
    'Bevan Dufty':559411,
    'David Chiu':501527,
    'Dennis Herrera':586941,
    'Ed Lee':0,
    'Jeff Adachi':0,
    'Joanna Rees':478231,
    'John Avalos':273000,
    'Leland Yee':490186,
    'Michela Alioto-Pier':456755,
    'Phil Ting':186484,
    'Terry Baum':0,
    'Tony Hall':310140,
    'Wilma Pang':0
    }
    
    for key in contribs.keys():
        candidate = Candidate.objects.get(entity__full_name__name=key)
        candidate.other_financing = Decimal(str(contribs[key]))
        candidate.public_financing = Decimal(str(public_finance[key]))
        candidate.save()


def filing_two():
    my_candidate = get_or_create_candidate('Jeff Adachi')
    candidate_alias = get_or_create_alias('Adachi For Mayor 2011', my_candidate)
    my_candidate.save()


    my_candidate = get_or_create_candidate('Ed Lee')
    candidate_alias = get_or_create_alias('Ed Lee for Mayor 2011', my_candidate)
    my_candidate.save()


    my_candidate = get_or_create_candidate('Terry Baum')
    candidate_alias = get_or_create_alias('Terry Baum for Mayor 2011', my_candidate)
    my_candidate.save()


    contributions('dataapps/sfmayor2011/data/10012011campaigndb.csv')

def dufty():
    #my_candidate = get_or_create_candidate('Bevan Dufty')
    #candidate_alias = get_or_create_alias('Bevan Dufty for Mayor 2011', my_candidate)
    contributions('dataapps/sfmayor2011/data/DUFTY-09-10.csv')


def preload():
    topic, created = Topic.objects.get_or_create(name='test topic', description='test topic description')

    my_candidate = get_or_create_candidate('Dennis Herrera')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('Dennis Herrera for Mayor 2011', my_candidate)

    my_candidate = get_or_create_candidate('Leland Yee')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('LELAND YEE FOR MAYOR 2011 EXPLORATORY COMMITTEE', my_candidate)
    candidate_alias = get_or_create_alias('City Residents Supporting Leland Yee for Mayor 2011, sponsored by American Federation of State County and Municipal Employees AFL-CIO and AFSCME CA People', my_candidate)
    candidate_alias = get_or_create_alias('LELAND YEE FOR MAYOR 2011', my_candidate)

    my_candidate = get_or_create_candidate('Joanna Rees')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('Join Joanna Rees', my_candidate)
    candidate_alias = get_or_create_alias('Join Joanna Rees for Mayor 2011', my_candidate)

    my_candidate = get_or_create_candidate('Phil Ting')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('Phil Ting for Mayor 2011', my_candidate)


    my_candidate = get_or_create_candidate('Michela Alioto-Pier')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('Michela Alioto-Pier for Mayor 2011', my_candidate)
    my_candidate = get_or_create_candidate('Tony Hall')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('Tony Hall for Mayor 2011', my_candidate)
    my_candidate = get_or_create_candidate('Bevan Dufty')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('Bevan Dufty for Mayor', my_candidate)
    my_candidate = get_or_create_candidate('John Avalos')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('Avalos for Mayor 2011', my_candidate)
    my_candidate = get_or_create_candidate('David Chiu')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('David Chiu for Mayor 2011', my_candidate)

    my_candidate = get_or_create_candidate('Ed Lee')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('Progress for All', my_candidate)


    my_candidate = get_or_create_candidate('Wilma Pang')
    my_candidate.bio = "test bio zzzz"
    my_candidate.topics.add(topic)
    my_candidate.save()
    candidate_alias = get_or_create_alias('Wilma Pang for Mayor 2011', my_candidate)


def contract_violations(filename=None):
    mines = {}
    exclude = set(string.punctuation)
    if filename != None:
        fin = list(csv.reader(open(filename, 'rb')))
    else:
        fin = list(csv.reader(open('dataapps/sfmayor2011/data/lee_contract_violations.csv', 'rb')))

    contribs = Contribution.objects.all().values_list('employer__slug')
    c_names = list()
    for c in contribs: c_names.append(c[0])
    names = list()
    for f in fin[1:]: names.append(slugify(f[3]))
    
    #c3 = [filter(lambda x: x in names, sublist) for sublist in contribs]

    for n in names:
        if n in c_names:
            objs = Contribution.objects.filter(employer__slug=n)
            mines[n] = objs
    return mines
            

def contributions(filename=None):
    if filename != None:
        fin = list(csv.reader(open(filename, 'rb')))
    else:
        fin = list(csv.reader(open('dataapps/sfmayor2011/data/08022011campaigndb.csv', 'rb')))
    for i,f in enumerate(fin[1:]):
        candidate_str = f[0]
        tran_date = f[1]
        contributor = f[2]
        street = f[3] + ' ' + f[4]
        city = f[5]
        state = f[6]
        zip = f[7]
        employer = f[8]
        occupation = f[9]
        amt = f[10]
   
        #candidates are referred to by their aliases in this file 
        candidate_o = get_candidate_by_alias(candidate_str)
        if candidate_o == None:
            print 'error finding candidate name=%s idx=%s' % (candidate_str,i)
        else:
            try:
                tran_date_split = tran_date.split(' ')
                if tran_date_split != '':
                    tran_datetime = datetime.strptime(tran_date_split[0], '%m/%d/%Y')

                
                contributor_n, created = Name.objects.get_or_create(name=contributor)
                
                occupation_o, created = Name.objects.get_or_create(name=occupation)
                
                employer_n, created = Name.objects.get_or_create(name=employer)
                
                place_o, created = Place.objects.get_or_create(street=street, city=city,\
                 state=state, zip=zip)
                
                contributor_o, created = Entity.objects.get_or_create(full_name=contributor_n, address=place_o)

                #amounts = amt.split('$')

                #amt = amounts[1]

                if '(' in amt:
                    amt = amt.replace('(', '')

                if ')' in amt:
                    amt = '-' + amt.replace(')', '')

                contribution = Contribution(contributor=contributor_o, candidate=candidate_o,\
                 employer=employer_n, occupation=occupation_o, amount=amt, date=tran_datetime, place=place_o)
                
                contribution.save()
            except Exception as e:
                print "exception=%s amt=%s idx=%s candidate=%s" % (e, amt, i, candidate_str)
        
