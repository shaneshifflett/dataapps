"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

from rankedvotes import loaders
from rankedvotes.models import Race

from rankedchoice import rcv_calculator

def race_one():
    #simple test to show first and second choices are working
    try:
        race = Race.objects.get(name='Test One')
    except:
        loaders.test_scenario_one()
    rcv_calculator.do_rcv('Test One')

def race_two():
    #test to show we exhaust all votes and store the count properly
    try:
        race = Race.objects.get(name='Test Two')
    except:
        loaders.test_scenario_two()
    rcv_calculator.do_rcv('Test Two')

def race_three():
    #two candidates are eleminated
    try:
        race = Race.objects.get(name='Test Three')
    except:
        loaders.test_scenario_three()
    rcv_calculator.do_rcv('Test Three')

def race_four():
    #simultaneously eleminte 2 candidates in second round
    try:
        race = Race.objects.get(name='Test Four')
    except:
        loaders.test_scenario_four()
    rcv_calculator.do_rcv('Test Four')
