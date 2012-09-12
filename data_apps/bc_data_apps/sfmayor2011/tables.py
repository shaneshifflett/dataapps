import django_tables as tables
from sfmayor2011.models import Contribution


class ContributionTable(tables.ModelTable):
    date = tables.Column(data='date')
    contributor = tables.Column(data='contributor__full_name__name')
    candidate = tables.Column(data='candidate__entity__full_name__name')
    employer = tables.Column(data='employer__name')
    occupation = tables.Column(data='occupation__name')
    city = tables.Column(data='place__city')
    state = tables.Column(data='place__state')
    amount = tables.Column(data='amount')
