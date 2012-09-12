from rankedvotes.models import *
from django.db import transaction, connection
from datetime import datetime
from django.db.models import Q
from csv import reader
from sets import Set
import operator
import csv


def precinct_cnt(race_name, winner_name):
    race = Race.objects.get(name=race_name)
    precincts = RankedBallot.objects.filter(race=race).values_list('precinct_str').distinct()

    undervote_c = Candidate.objects.get(name='undervote', race=race)
    overvote_c = Candidate.objects.get(name='overvote', race=race)

    winner = Candidate.objects.get(name=winner_name, race=race)
    print 'precinct, total, exhausted, one_unique, two_unique, three_unique, undervotes, overvotes, dupes, blanks, winner_cnt'
    for p in precincts:
        try:
            total = RankedBallot.objects.filter(race=race, precinct_str=p[0]).count()

            exhausted_ballots = RankedBallot.objects.filter(race=race,precinct_str=p[0],was_exhausted=True).count()
            ballots = RankedBallot.objects.filter(race=race, precinct_str=p[0])
            #store cnt of unique choices
            #0 element = cnt of one unique choices
            #1 element = cnt of two unique choices, etc
            uniqueness = [0,0,0,0]
            dupes_cnt = 0
            blanks_cnt = 0
            slates = {}
            first_choice = {}
            second_choice = {}

            for b in ballots:
                cnt = b.unique_choices_cnt()
                uniqueness[cnt] += 1

                if b.has_duplicate_choices():
                    dupes_cnt += 1
                if b.has_blank_choices():
                    blanks_cnt +=1

                try:
                    slates[b.get_slate()] += 1
                except KeyError:
                    slates[b.get_slate()] = 1

                choices = b.get_slate().split(',')

                if len(choices) > 0:
                    try:
                        first_choice[choices[0]] += 1
                    except KeyError:
                        first_choice[choices[0]] = 1

                if len(choices) > 1:
                    try:
                        second_choice[choices[1]] += 1
                    except KeyError:
                        second_choice[choices[1]] = 1

            slates = sorted(slates.iteritems(), key=operator.itemgetter(1), reverse=True)
            slates_to_save = list()
            for s in slates[0:5]:
                nvp = NameValuePair(name=s[0], value_one=s[1])
                nvp.save(using='boundary_db')
                slates_to_save.append(nvp)
       
            firsts = sorted(first_choice.iteritems(), key=operator.itemgetter(1), reverse=True)
            firsts_to_save = list()
            for f in firsts[0:5]:
                nvp = NameValuePair(name=f[0], value_one=f[1])
                try:
                    second = second_choice[f[0]]
                except KeyError:
                    second = 0
                nvp.value_two = second
                nvp.save(using='boundary_db')
                firsts_to_save.append(nvp)

            first_choice = RankedBallot.objects.filter(race=race, precinct_str=p[0], choice_one=winner).exclude(Q(choice_two=overvote_c)|Q(choice_three=overvote_c)).count()
            undervotes = RankedBallot.objects.filter(race=race, precinct_str=p[0],choice_one=undervote_c, choice_two=undervote_c, choice_three=undervote_c).count()
            overvotes = RankedBallot.objects.filter(Q(choice_one=overvote_c)|Q(choice_two=overvote_c)|Q(choice_three=overvote_c)).filter(race=race, precinct_str=p[0]).count()

            precinct = p[0].split('Pct ')[1]
            pct = precinct.split(' MB')[0]

            b = PrecinctAnalysis(precinct=pct, exhausted=exhausted_ballots,\
             total=total, one_unique=uniqueness[1], two_unique=uniqueness[2], three_unique=uniqueness[3],\
             undervotes=undervotes, overvotes=overvotes, duplicates=dupes_cnt, blanks=blanks_cnt,\
             first_choice=first_choice, race_name=race_name)
            b.save(using='boundary_db')
            b.slate_counts = slates_to_save
            b.candidate_counts = firsts_to_save

            print '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (p[0], total, exhausted_ballots, uniqueness[1], uniqueness[2], uniqueness[3], undervotes, overvotes, dupes_cnt, blanks_cnt, first_choice)

        except Exception as e:
            print e
            #import pdb;pdb.set_trace()


def import_ballot_analysis(race_name, filename):
    filename = filename
    rows = list(reader(open(filename, 'rb')))
    for row in rows[1:]:
        precinct = row[0].split('Pct ')[1]
        pct = precinct.split(' MB')[0]
        b = PrecinctAnalysis(precinct=pct, exhausted=row[2],\
         total=row[1], one_unique=row[3], two_unique=row[4], three_unique=row[5],\
         undervotes=row[6], overvotes=row[7], duplicates=row[8], blanks=row[9],\
         first_choice=row[10], race_name=race_name)
        b.save(using='boundary_db')


def add_overunder_voters(race_name):
    race = Race.objects.get(name=race_name)
    candidates = {
        '00000001':'overvote',
        '00000010':'undervote',
    }

    #store candidate pk ids
    candidate_pk_ids = {}
    for key in candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate.id

def sciences_event():
    m_date = datetime(2011,10,19)
    race, created = Race.objects.get_or_create(name='Academy of Sciences',\
     date=m_date, city='San Francisco', state='CA')
    choices = {
        'G': 'Giraffe',
        'A': 'Alligator',
        'P': 'Penguin',
        'J': 'Jaguar',
        'S': 'Spider'
    }
    #store candidate pk ids
    for key in choices.keys():
        candidate, created = Candidate.objects.get_or_create(name=choices[key],\
         race=race)

def load_oakland():
    m_date = datetime(2010,11,8)
    ballots = oakland()
    race = Race.objects.get(name='Oakland 2010 Mayoral',\
     date=m_date, city='Oakland', state='CA')
    save_votes(votes, race.id)

def test_scenario_three():
    m_date = datetime(2010,11,8)
    now = datetime.now()
    race, created = Race.objects.get_or_create(name='Test Three',\
     date=m_date, city='Oakland', state='CA')

    
    a, created = Candidate.objects.get_or_create(name='A',\
     race=race)
    b, created = Candidate.objects.get_or_create(name='B',\
     race=race)
    c, created = Candidate.objects.get_or_create(name='C',\
     race=race)
    d, created = Candidate.objects.get_or_create(name='D',\
     race=race)
    e, created = Candidate.objects.get_or_create(name='E',\
     race=race)

    votes = {}

    #first second third choice matters for 1st choice candidate e
    ballot = {'file_id':'01', 'choice_one':e.id, 'choice_two':d.id, 'choice_three':c.id}
    votes['-1'] = ballot

    ballot = {'file_id':'01', 'choice_one':e.id, 'choice_two':c.id, 'choice_three':b.id}
    votes['-2'] = ballot


    #only first and second choice votes matter for 1st choice candidate d
    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['1'] = ballot

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['2'] = ballot 

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':c.id, 'choice_three':a.id}
    votes['3'] = ballot                                        

    #only first and second choice votes matter for 1st choice candidate c

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['4'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['5'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['6'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['7'] = ballot

    #only first choice matter for 1st choice candidate b

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['8'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['9'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['10'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['11'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['12'] = ballot

    #only first choice matters for 1st choice candidate a
    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['13'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['14'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['15'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['16'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['17'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['18'] = ballot

    save_votes(votes, race.id)


def test_scenario_four():
    m_date = datetime(2010,11,8)
    now = datetime.now()
    race, created = Race.objects.get_or_create(name='Test Four',\
     date=m_date, city='Oakland', state='CA')

    
    a, created = Candidate.objects.get_or_create(name='A',\
     race=race)
    b, created = Candidate.objects.get_or_create(name='B',\
     race=race)
    c, created = Candidate.objects.get_or_create(name='C',\
     race=race)
    d, created = Candidate.objects.get_or_create(name='D',\
     race=race)
    e, created = Candidate.objects.get_or_create(name='E',\
     race=race)

    votes = {}

    #first second third choice matters for 1st choice candidate e
    ballot = {'file_id':'01', 'choice_one':e.id, 'choice_two':d.id, 'choice_three':b.id}
    votes['-1'] = ballot

    ballot = {'file_id':'01', 'choice_one':e.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['-2'] = ballot


    #only first and second choice votes matter for 1st choice candidate d
    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['1'] = ballot

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['2'] = ballot 

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':a.id}
    votes['3'] = ballot                                        

    #only first and second choice votes matter for 1st choice candidate c

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['4'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['5'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['6'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['7'] = ballot

    #only first choice matter for 1st choice candidate b

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['8'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['9'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['10'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['11'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['12'] = ballot

    #only first choice matters for 1st choice candidate a
    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['13'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['14'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['15'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['16'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['17'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['18'] = ballot

    save_votes(votes, race.id)


def test_scenario_three():
    m_date = datetime(2010,11,8)
    now = datetime.now()
    race, created = Race.objects.get_or_create(name='Test Two',\
     date=m_date, city='Oakland', state='CA')

    
    a, created = Candidate.objects.get_or_create(name='A',\
     race=race)
    b, created = Candidate.objects.get_or_create(name='B',\
     race=race)
    c, created = Candidate.objects.get_or_create(name='C',\
     race=race)
    d, created = Candidate.objects.get_or_create(name='D',\
     race=race)
    e, created = Candidate.objects.get_or_create(name='E',\
     race=race)

    votes = {}

    #first second third choice matters for 1st choice candidate e
    ballot = {'file_id':'01', 'choice_one':e.id, 'choice_two':d.id, 'choice_three':c.id}
    votes['-1'] = ballot

    ballot = {'file_id':'01', 'choice_one':e.id, 'choice_two':c.id, 'choice_three':b.id}
    votes['-2'] = ballot


    #only first and second choice votes matter for 1st choice candidate d
    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['1'] = ballot

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['2'] = ballot 

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['3'] = ballot                                        

    #only first and second choice votes matter for 1st choice candidate c

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['4'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['5'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['6'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['7'] = ballot

    #only first choice matter for 1st choice candidate b

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['8'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['9'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['10'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['11'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['12'] = ballot

    #only first choice matters for 1st choice candidate a
    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['13'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['14'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['15'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['16'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['17'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['18'] = ballot

    save_votes(votes, race.id)


def test_scenario_two():
    m_date = datetime(2010,11,8)
    now = datetime.now()
    race, created = Race.objects.get_or_create(name='Test Two',\
     date=m_date, city='Oakland', state='CA')

    
    a, created = Candidate.objects.get_or_create(name='A',\
     race=race)
    b, created = Candidate.objects.get_or_create(name='B',\
     race=race)
    c, created = Candidate.objects.get_or_create(name='C',\
     race=race)
    d, created = Candidate.objects.get_or_create(name='D',\
     race=race)
    e, created = Candidate.objects.get_or_create(name='E',\
     race=race)

    votes = {}

    #first second third choice matters for 1st choice candidate e
    ballot = {'file_id':'01', 'choice_one':e.id, 'choice_two':d.id, 'choice_three':c.id}
    votes['-1'] = ballot

    ballot = {'file_id':'01', 'choice_one':e.id, 'choice_two':c.id, 'choice_three':b.id}
    votes['-2'] = ballot


    #only first and second choice votes matter for 1st choice candidate d
    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['1'] = ballot

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['2'] = ballot 

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['3'] = ballot                                        

    #only first and second choice votes matter for 1st choice candidate c

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['4'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['5'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['6'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['7'] = ballot

    #only first choice matter for 1st choice candidate b

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['8'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['9'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['10'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['11'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['12'] = ballot

    #only first choice matters for 1st choice candidate a
    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['13'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['14'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['15'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['16'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['17'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['18'] = ballot

    save_votes(votes, race.id)

def test_scenario_five():
    m_date = datetime(2010,11,8)
    now = datetime.now()
    race, created = Race.objects.get_or_create(name='Test Five',\
     date=m_date, city='Oakland', state='CA')

    
    a, created = Candidate.objects.get_or_create(name='A',\
     race=race)
    b, created = Candidate.objects.get_or_create(name='B',\
     race=race)
    c, created = Candidate.objects.get_or_create(name='C',\
     race=race)
    d, created = Candidate.objects.get_or_create(name='D',\
     race=race)

    votes = {}

    #only first and second choice votes matter for 1st choice candidate d
    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['1'] = ballot

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['2'] = ballot 

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['3'] = ballot                                        

    #only first and second choice votes matter for 1st choice candidate c

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['4'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['5'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['6'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['7'] = ballot

    #only first choice matter for 1st choice candidate b

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['8'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['9'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['10'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['11'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['12'] = ballot

    #only first choice matters for 1st choice candidate a
    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['13'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['14'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['15'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['16'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['17'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['18'] = ballot

    save_votes(votes, race.id)

def test_scenario_one():
    m_date = datetime(2010,11,8)
    now = datetime.now()
    race, created = Race.objects.get_or_create(name='Test One',\
     date=m_date, city='Oakland', state='CA')

    
    a, created = Candidate.objects.get_or_create(name='A',\
     race=race)
    b, created = Candidate.objects.get_or_create(name='B',\
     race=race)
    c, created = Candidate.objects.get_or_create(name='C',\
     race=race)
    d, created = Candidate.objects.get_or_create(name='D',\
     race=race)

    votes = {}

    #only first and second choice votes matter for 1st choice candidate d
    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['1'] = ballot

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['2'] = ballot 

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['3'] = ballot                                        

    #only first and second choice votes matter for 1st choice candidate c

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['4'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['5'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['6'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['7'] = ballot

    #only first choice matter for 1st choice candidate b

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['8'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['9'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['10'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['11'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['12'] = ballot

    #only first choice matters for 1st choice candidate a
    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['13'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['14'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['15'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['16'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['17'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['18'] = ballot

    save_votes(votes, race.id)

def test_scenario_one():
    m_date = datetime(2010,11,8)
    now = datetime.now()
    race, created = Race.objects.get_or_create(name='Test One',\
     date=m_date, city='Oakland', state='CA')

    
    a, created = Candidate.objects.get_or_create(name='A',\
     race=race)
    b, created = Candidate.objects.get_or_create(name='B',\
     race=race)
    c, created = Candidate.objects.get_or_create(name='C',\
     race=race)
    d, created = Candidate.objects.get_or_create(name='D',\
     race=race)

    votes = {}

    #only first and second choice votes matter for 1st choice candidate d
    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['1'] = ballot

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['2'] = ballot 

    ballot = {'file_id':'01', 'choice_one':d.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['3'] = ballot                                        

    #only first and second choice votes matter for 1st choice candidate c

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['4'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['5'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['6'] = ballot

    ballot = {'file_id':'01', 'choice_one':c.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['7'] = ballot

    #only first choice matter for 1st choice candidate b

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['8'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['9'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['10'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['11'] = ballot

    ballot = {'file_id':'01', 'choice_one':b.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['12'] = ballot

    #only first choice matters for 1st choice candidate a
    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['13'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['14'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':a.id, 'choice_three':b.id}
    votes['15'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['16'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['17'] = ballot

    ballot = {'file_id':'01', 'choice_one':a.id, 'choice_two':b.id, 'choice_three':b.id}
    votes['18'] = ballot

    save_votes(votes, race.id)



def poll():
    ballots = baycitizen_poll()
    m_date = datetime(2011,10,14)
    race = Race.objects.get(name='Bay Citizen USF Mayoral Poll',\
     date=m_date, city='San Francisco', state='CA')
    votes = baycitizen_poll()
    #save_votes(votes, race.id)

def get_rcv_keys(filename=None):
    if filename != None:
        fin = list(csv.reader(open(filename, 'rb')))
    else:
        fin = list(csv.reader(open('dataapps/rankedvotes/data/rcvsim.csv', 'rb')))

    c1_keys = {}
    c2_keys = {}
    c3_keys = {}

    for i,f in enumerate(fin[1:]):
        c1 = f[0]
        c2 = f[1]
        c3 = f[2]
        c1_keys[c1] = c1
        c2_keys[c2] = c2
        c3_keys[c3] = c3

    print 'c1'
    for key in c1_keys.keys():
        print '"%s":' % key

    print 'c2'
    for key in c2_keys.keys():
        print '"%s":' % key

    print 'c3'
    for key in c3_keys.keys():
        print '"%s":' % key

def da_race(filename=None):
    sf_candidates = {
        "Bock":"Sharmin Bock",
        "Fazio": "Bill Fazio",
        "Gascon": "George Gascon",
        "Onek": "David Onek",
        "Vu Vuon": "Vu Vuon Trinh"
    }

    m_date = datetime(2011,10,17)
    now = datetime.now()
    race, created = Race.objects.get_or_create(name='Bay Citizen USF District Attorney Poll',\
     date=m_date, city='San Francisco', state='CA')


    #store candidate pk ids
    candidate_pk_ids = {}
    for key in sf_candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=sf_candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate
    if filename != None:
        fin = list(csv.reader(open(filename, 'rb')))
    else:
        fin = list(csv.reader(open('dataapps/rankedvotes/data/DArcv.csv', 'rb')))


    votes = {}
    for i,f in enumerate(fin[1:]):
        voter_id = f[0]
        choice_one = f[1]
        choice_two = f[2]
        choice_three = f[3]

        
        if choice_one == 'NA':
            choice_one = None
        else:
            choice_one = candidate_pk_ids[choice_one]
        if choice_two == 'NA':
            choice_two = None
        else:
            choice_two = candidate_pk_ids[choice_two]
        if choice_three == 'NA':
            choice_three = None
        else:
            choice_three = candidate_pk_ids[choice_three]

        rb = RankedBallot(file_id=voter_id, choice_one=choice_one,\
         choice_two=choice_two, choice_three=choice_three,\
         race=race).save()

def baycitizen_poll(filename=None):

    sf_candidates = {
        "Ting": "Phil Ting",
        " Lee": "Ed Lee",
        "Rees": "Joanna Rees",
        "Dufty": "Bevan Dufty",
        "Herrera": "Dennis Herrera",
        "Yee": "Leland Yee",
        "Avalos": "John Avalos",
        "Chiu": "David Chiu",
        "Adachi": "Jeff Adachi",
        "Alioto-Pier":"Michela Alioto-Pier",
        "Other": "Other",
        "Hall":"Tony Hall"
    }

    m_date = datetime(2011,10,14)
    now = datetime.now()
    race, created = Race.objects.get_or_create(name='Bay Citizen USF Mayoral Poll',\
     date=m_date, city='San Francisco', state='CA')


    #store candidate pk ids
    candidate_pk_ids = {}
    for key in sf_candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=sf_candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate
    if filename != None:
        fin = list(csv.reader(open(filename, 'rb')))
    else:
        fin = list(csv.reader(open('dataapps/rankedvotes/data/rcvsim.csv', 'rb')))

    votes = {}
    for i,f in enumerate(fin[1:]):
        voter_id = i
        choice_one = f[0]
        choice_two = f[1]
        choice_three = f[2]

        
        if choice_one == 'NA':
            choice_one = None
        else:
            choice_one = candidate_pk_ids[choice_one]
        if choice_two == 'NA':
            choice_two = None
        else:
            choice_two = candidate_pk_ids[choice_two]
        if choice_three == 'NA':
            choice_three = None
        else:
            choice_three = candidate_pk_ids[choice_three]

        rb = RankedBallot(file_id=voter_id, choice_one=choice_one,\
         choice_two=choice_two, choice_three=choice_three,\
         race=race).save()

        """
        if voter_id in votes.keys():
            ballot = votes[voter_id]
        else:
            ballot = {'file_id':voter_id, 'choice_one':choice_one,\
             'choice_two':choice_two, 'choice_three':choice_three}
        
        votes[voter_id] = ballot

        """
    for i in range(0,105):
        #create the undecided/no response ballots
        choice_one = None
        choice_two = None
        choice_three = None
        rb = RankedBallot(file_id=voter_id, choice_one=choice_one,\
         choice_two=choice_two, choice_three=choice_three,\
         race=race).save()
    return votes

def sf_supervisors_d6_2010():
    """
    overvote: a ballot where more than one candidate is choosen for the same rank
    undervote: a ballot where the voter did not choose a candidate for that rank
    http://archive.fairvote.org/media/documents/rcv-election-guidelines.pdf
    """
    m_date = datetime(2010,11,2)
    now = datetime.now()
    race, created = Race.objects.get_or_create(name='SF Supervisors District 6 2010',\
     date=m_date, city='San Francisco', state='CA', type='supervisors', headline='San Fancisco District 6 Supervisors Race 2010')

    candidates = {
        '0000128':'Dean Clark',
        '0000129':'Debra Walker',
        '0000130':'James Keys',
        '0000131':'Jane Kim',
        '0000132':'H. Brown',
        '0000133':'George VAZHAPPALLY',
        '0000134':'Theresa Sparks',
        '0000135':'Fortunate Nate Payne',
        '0000136':'Elaine Zamora',
        '0000137':'Jim Meko',
        '0000138':'Matt Ashe',
        '0000139':'Matt Drake',
        '0000140':'George Davis',
        '0000141':'Glendon Anna Conda Hyde',
        '0000023':'Write-in',
        '00000001':'overvote',
        '00000010':'undervote',
    }

    #store candidate pk ids
    candidate_pk_ids = {}
    for key in candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate.id

    return read_ballotimage('dataapps/rankedvotes/data/sf_supervisors_district_6_2010.txt', candidate_pk_ids)

def oakland_mayoral_2010():
    """
    overvote: a ballot where more than one candidate is choosen for the same rank
    undervote: a ballot where the voter did not choose a candidate for that rank
    http://archive.fairvote.org/media/documents/rcv-election-guidelines.pdf
    """
    oakland_candidates = {
        '0000393':'Don Perata',
        '0000394':'Terence Candell',
        '0000395':'Greg Harland',
        '0000396':'Don Macleay',
        '0000397':'Jean Quan',
        '0000398':'Arnold Fields',
        '0000399':'Joe Tuman',
        '0000400':'Marcie Hodge',
        '0000401':'Larry Lionel LL Young Jr',
        '0000402':'Rebecca Kaplan',
        '0000087':'Write-In',
        '00000001':'overvote',
        '00000010':'undervote',
    }
    m_date = datetime(2010,11,19)
    race, created = Race.objects.get_or_create(name='Oakland Mayoral 2010',\
     date=m_date, city='Oakland', state='CA', type='mayoral', headline='Oakland Mayoral Race 2010')

    #store candidate pk ids
    candidate_pk_ids = {}
    for key in oakland_candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=oakland_candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate.id

    return read_ballotimage('dataapps/rankedvotes/data/oakland_mayoral_2010.txt', candidate_pk_ids)


def oakland_for_perata():
    """
    overvote: a ballot where more than one candidate is choosen for the same rank
    undervote: a ballot where the voter did not choose a candidate for that rank
    http://archive.fairvote.org/media/documents/rcv-election-guidelines.pdf
    """
    oakland_candidates = {
        '0000393':'Don Perata',
        '0000394':'Terence Candell',
        '0000395':'Greg Harland',
        '0000396':'Don Macleay',
        '0000397':'Jean Quan',
        '0000398':'Arnold Fields',
        '0000399':'Joe Tuman',
        '0000400':'Marcie Hodge',
        '0000401':'Larry Lionel LL Young Jr',
        '0000402':'Rebecca Kaplan',
        '0000087':'Write-In',
        '00000001':'overvote',
        '00000010':'undervote',
    }
    m_date = datetime(2010,11,19)
    race, created = Race.objects.get_or_create(name='Oakland Alternate Mayoral 2010',\
     date=m_date, city='Oakland', state='CA', type='mayoral', headline='Oakland\' Other Mayoral Race 2010')

    #store candidate pk ids
    candidate_pk_ids = {}
    for key in oakland_candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=oakland_candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate.id

    votes = read_ballotimage('dataapps/rankedvotes/data/oakland_mayoral_2010.txt', candidate_pk_ids)

    choice_one = candidate_pk_ids['0000402']

    print 'starting to process kaplan votes'

    for i in xrange(1,2401):
        voter_id = -1*int(i)
        precinct_id = '1111'
        ballot = {'file_id':str(voter_id), 'choice_one':choice_one, 'choice_two':None, 'choice_three':None, 'precinct':precinct_id}
        votes[voter_id] = ballot

    return votes

def sf_supervisors_d2_2010(filename=None):
    """
    overvote: a ballot where more than one candidate is choosen for the same rank
    undervote: a ballot where the voter did not choose a candidate for that rank
    http://archive.fairvote.org/media/documents/rcv-election-guidelines.pdf
    """
    m_date = datetime(2010,11,2)
    race, created = Race.objects.get_or_create(name='SF Supervisors District 2 2010',\
     date=m_date, city='San Francisco', state='CA', type='supervisors', headline='San Francisco District 2 Supervisors Race 2010')

    candidates = {
        '0000120':'Janet Reilly',
        '0000121':'Vilma B. Guinto Peoro',
        '0000122':'Barbara Berwick',
        '0000123':'Mark Farrell',
        '0000124':'Abraham Simmons',
        '0000126':'Kat Anderson',
        '0000025':'Write-in',
        '00000001':'overvote',
        '00000010':'undervote',
    }

    #store candidate pk ids
    candidate_pk_ids = {}
    for key in candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate.id
    
    return read_ballotimage('dataapps/rankedvotes/data/sf_supervisors_district_2_2010.txt', candidate_pk_ids)


def sf_supervisors_d8_2010(filename=None):
    """
    overvote: a ballot where more than one candidate is choosen for the same rank
    undervote: a ballot where the voter did not choose a candidate for that rank
    http://archive.fairvote.org/media/documents/rcv-election-guidelines.pdf
    """
    m_date = datetime(2010,11,2)
    race, created = Race.objects.get_or_create(name='SF Supervisors District 8 2010',\
     date=m_date, city='San Francisco', state='CA', type='supervisors', headline='San Francisco District 8 Supervisors Race 2010')

    candidates = {
        '0000142':'Scott Wiener',
        '0000143':'Rebecca Prozan',
        '0000144':'Rafael Mandelman',
        '0000145':'Bill Hemenger',
        '0000022':'Write-in',
        '00000001':'overvote',
        '00000010':'undervote',
    }

    #store candidate pk ids
    candidate_pk_ids = {}
    for key in candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate.id
    
    return read_ballotimage('dataapps/rankedvotes/data/sf_supervisors_district_8_2010.txt', candidate_pk_ids)


def sf_supervisors_d10_2010(filename=None):
    """
    overvote: a ballot where more than one candidate is choosen for the same rank
    undervote: a ballot where the voter did not choose a candidate for that rank
    http://archive.fairvote.org/media/documents/rcv-election-guidelines.pdf
    """
    m_date = datetime(2010,11,2)
    race, created = Race.objects.get_or_create(name='SF Supervisors District 10 2010',\
     date=m_date, city='San Francisco', state='CA', type='supervisors', headline='San Francisco District 10 Supervisors Race 2010')

    candidates = {
        '0000146':'Ashley H. Rhodes',
        '0000147':'Marlene Tran',
        '0000148':'Malia Cohen',
        '0000149':'James M. Calloway',
        '0000150':'Stephen Weber',
        '0000151':'Diane Wesley Smith',
        '0000152':'Tony Kelly',
        '0000153':'Kristine Enea',
        '0000154':'Nyese Joshua',
        '0000155':'Ellsworth Ell Jennison',
        '0000156':'Chris Jackson',
        '0000157':'Dewitt M. Lacy',
        '0000158':'M.J. Marie Franklin',
        '0000159':'Lynette Sweet',
        '0000160':'Eric Smith',
        '0000161':'Jackie Norman',
        '0000162':'Geoffrea Morris',
        '0000163':'Steve Moss',
        '0000164':'Ed Donaldson',
        '0000165':'Teresa Duque',
        '0000166':'Rodney Hampton, Jr.',
        '0000026':'Write-in',
        '00000001':'overvote',
        '00000010':'undervote',
    }

    #store candidate pk ids
    candidate_pk_ids = {}
    for key in candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate.id
    
    return read_ballotimage('dataapps/rankedvotes/data/sf_supervisors_district_10_2010.txt', candidate_pk_ids)


def get_slates_by_race_exhausted(race_name):
    race = Race.objects.get(name=race_name)
    slates = {}
    ballots = RankedBallot.objects.filter(race=race, was_exhausted=True)
    for b in ballots:
        candidates = b.get_slate().split(',')
        c_set = Set(candidates)
        slate = ','.join(c_set)
        try:
            slates[slate] += 1
        except KeyError:
            slates[slate] = 1
   
    for key in slates.keys():
        print "%s,%s" % (key, slates[key])

def get_slates_by_race(race_name):
    race = Race.objects.get(name=race_name)
    slates = {}
    ballots = RankedBallot.objects.filter(race=race)
    for b in ballots:
        try:
            slates[b.get_slate()] += 1
        except KeyError:
            slates[b.get_slate()] = 1
   
    for key in slates.keys():
        print "%s,%s" % (key, slates[key])


def get_slates_by_candidate(race_name,candidate_name):
    race = Race.objects.get(name=race_name)
    candidate = Candidate.objects.get(race=race, name=candidate_name)
    slates = {}
    ballots = RankedBallot.objects.filter(Q(choice_one=candidate)|Q(choice_two=candidate)|Q(choice_three=candidate)).filter(race=race)
    for b in ballots:
        try:
            slates[b.get_slate()] += 1
        except KeyError:
            slates[b.get_slate()] = 1
    
    for key in slates.keys():
        print "%s,%s" % (key, slates[key])


def get_slates_sin_undervotes(race_name):
    race = Race.objects.get(name=race_name)
    candidate = Candidate.objects.get(race=race, name='undervote')
    slates = {}
    ballots = RankedBallot.objects.filter(race=race).exclude(Q(choice_one=candidate)|Q(choice_two=candidate)|Q(choice_three=candidate)).exclude(choice_one__name='Ed Lee')
    for b in ballots:
        try:
            slates[b.get_slate()] += 1
        except KeyError:
            slates[b.get_slate()] = 1
    
    for key in slates.keys():
        print "%s,%s" % (key, slates[key])



def associate_precincts(race_name, filename=None):
    if filename == None:
        filename='dataapps/rankedvotes/data/Mayor-MasterLookUp.txt'
    file = open(filename,'rb')
    race = Race.objects.get(name=race_name)
    while True:
        line = file.readline()
        if len(line) <= 0:
            break

        type = line[0:10].strip()

        if type == 'Precinct':
            p_key = line[10:17]
            p_val = line[17:30]

            rbs = RankedBallot.objects.filter(race__name=race_name,precinct_master_lookup=p_key)

            print 'key=%s val=%s' % (p_key, p_val)
            for r in rbs:
                r.precinct_str = p_val.strip()
                r.save()

def sf_mayor_2011(filename=None):
    """
    overvote: a ballot where more than one candidate is choosen for the same rank
    undervote: a ballot where the voter did not choose a candidate for that rank
    http://archive.fairvote.org/media/documents/rcv-election-guidelines.pdf
    """
    m_date = datetime(2011,11,8)
    race, created = Race.objects.get_or_create(name='San Francisco Mayoral Race 2011',\
     date=m_date, city='San Francisco', state='CA', type='mayor')

    RankedBallot.objects.filter(race=race).delete()

    candidates = {
        '0000029':'Leland Yee',
        '0000030':'David Chiu',
        '0000031':'Paul Currier',
        '0000032':'Tony Hall',
        '0000033':'Dennis Herrera',
        '0000034':'Phil Ting',
        '0000035':'Terry Joan Baum',
        '0000036':'Cesar Ascarrunz',
        '0000037':'John Avalos',
        '0000038':'Michela Alioto-Pier',
        '0000039':'Jeff Adachi',
        '0000040':'Emil Lawrence',
        '0000041':'Ed Lee',
        '0000042':'Joanna Rees',
        '0000043':'Bevan Dufty',
        '0000044':'Wilma Pang',
        '0000003':'Write-in',
        '0000045':'John Edward Fitch',
        '0000046':'Gilbert Louis Francis',
        '0000047':'Rodney Hauge',
        '0000048':'Robert Johnson',
        '0000049':'Harold Miller',
        '0000050':'Patrick Monette-Shaw',
        '0000051':'Lea Sherman',
        '0000052':'David Villa-Lobos',
        '00000001':'overvote',
        '00000010':'undervote',
    }

    #store candidate pk ids
    candidate_pk_ids = {}
    for key in candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate.id
    
    return read_ballotimage('dataapps/rankedvotes/data/Mayor-BallotImage.txt', candidate_pk_ids)


def sf_sheriff_2011(filename=None):
    """
    overvote: a ballot where more than one candidate is choosen for the same rank
    undervote: a ballot where the voter did not choose a candidate for that rank
    http://archive.fairvote.org/media/documents/rcv-election-guidelines.pdf
    """
    m_date = datetime(2011,11,8)
    race, created = Race.objects.get_or_create(name='San Francisco Sheriffs Race 2011',\
     date=m_date, city='San Francisco', state='CA', type='sheriff')

    RankedBallot.objects.filter(race=race).delete()

    candidates = {
        '0000025':'Chris Cunnie',
        '0000026':'David Wong',
        '0000027':'Paul Miyamoto',
        '0000028':'Ross Mirkarimi',
        '0000002':'Write-in',
        '00000001':'overvote',
        '00000010':'undervote',
    }
    

    #store candidate pk ids
    candidate_pk_ids = {}
    for key in candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate.id
    
    return read_ballotimage('dataapps/rankedvotes/data/2011_sf_sheriff_ballotimage.txt', candidate_pk_ids)


def sf_da_2011(filename=None):
    """
    overvote: a ballot where more than one candidate is choosen for the same rank
    undervote: a ballot where the voter did not choose a candidate for that rank
    http://archive.fairvote.org/media/documents/rcv-election-guidelines.pdf
    """
    m_date = datetime(2011,11,8)
    race, created = Race.objects.get_or_create(name='San Francisco District Attorney Race 2011',\
     date=m_date, city='San Francisco', state='CA', type='district attorney')

    RankedBallot.objects.filter(race=race).delete()

    candidates = {
        '0000020':'Bill Fazio',
        '0000021':'David Onek',
        '0000022':'Vu Vuong Trinh',
        '0000023':'George Gascon',
        '0000024':'Sharmin Bock',
        '0000001':'Write-in',
        '00000001':'overvote',
        '00000010':'undervote',
    }

    #store candidate pk ids
    candidate_pk_ids = {}
    for key in candidates.keys():
        candidate, created = Candidate.objects.get_or_create(name=candidates[key],\
         race=race)
        candidate_pk_ids[key] = candidate.id
    
    return read_ballotimage('dataapps/rankedvotes/data/2011_sf_da_ballotimage.txt', candidate_pk_ids)


def read_ballotimage(filename, candidate_pk_ids):
    file = open(filename,'rb')
    #fin = list(csv.reader(open(filename, 'rb')))

    now = datetime.now()
    #gather all votes into a dict to save some time
    votes = {}
    overvotes = 0
    undervotes = 0
    not_in_contest = 0
    undervotes_d = {}
    overvotes_d = {}
    idx = 0
    #for i,f in enumerate(fin[0:]):
    while True:
        line_one = file.readline()
        print line_one
        if len(line_one) <= 0:
            break
        line_two = file.readline()
        line_three = file.readline()
        
        voter_id = line_one[7:16]
        voter_id2 = line_two[7:16]
        voter_id3 = line_three[7:16]

        if voter_id != voter_id2 != voter_id3:
            print 'bad voter id %s %s %s' % (voter_id, voter_id2, voter_id3)
            break
        
        #line = f[0]
        contest = line_one[0:7]
        precinct_id = line_one[26:33]

        lines = [line_one, line_two, line_three]

        for line in lines:

            rank = line[33:36]
            candidate_id = line[36:43]
            overvote = line[43]
            undervote = line[44]

            #this is an important conversion so we can make underover-votes a candidate
            #and thus throw exceptions in runtime so make sure your candidate id's match
            #what we set them to below
            if candidate_id == '0000000' and overvote == '1':
                candidate_id = '00000001'
            elif candidate_id == '0000000' and undervote == '1':
                candidate_id = '00000010'

            candidate = candidate_pk_ids[candidate_id]


            rank_val = int(rank)
            #retrieve a ballot or create a new one with the id of the ballot

            try:
                ballot = votes[voter_id]
            except KeyError:
                ballot = {'file_id':voter_id, 'choice_one':None, 'choice_two':None, 'choice_three':None, 'precinct':precinct_id}

            
            if rank_val == 1:
                ballot['choice_one'] = candidate
            elif rank_val == 2:
                ballot['choice_two'] = candidate
            elif rank_val == 3:
                ballot['choice_three'] = candidate
            else:
                print 'voter_id=%s line=%s rank=%s rank invald' % (voter_id, i, rank_val)
            
            #store result
            votes[voter_id] = ballot

        if idx%1000 == 0:
            #update us, 366k rows in this file
            delta = datetime.now() - now
            print 'line=%s elapsed=%s' % (idx, delta)
            now = datetime.now()

    print 'overvotes=%s undervotes=%s notincontest=%s' % (overvotes, undervotes, not_in_contest)

    return votes





@transaction.commit_manually
def save_votes(votes, race_id):
    """
    votes: dict of votes keyed by the voters id, it's value is the ballot
    race_id: race to assign the ballots to
    """
    now = datetime.now()
    #we're done gathering votes, loop through saving them    
    cursor = connection.cursor()
    ballot_insert_sql = "insert into rankedvotes_rankedballot(choice_one_id, choice_two_id, choice_three_id, file_id, race_id, precinct_master_lookup, was_exhausted) values(%s, %s, %s, %s, %s, %s, %s);" 
    for i, key in enumerate(votes.keys()):
        obj = votes[key]
        try:
            cursor.execute(ballot_insert_sql, [obj['choice_one'], obj['choice_two'], obj['choice_three'], obj['file_id'], race_id, obj['precinct'], False])
        except Exception as e:
            print 'obj=%s e=%s' % (obj, e)


        if i%1000 == 0:
            #update us, 366k rows in this file
            delta = datetime.now() - now
            print 'line=%s elapsed=%s' % (i, delta)
            now = datetime.now()
            if i != 0:
                transaction.commit()

    transaction.commit()


