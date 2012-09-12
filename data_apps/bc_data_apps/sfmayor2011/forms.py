from django import forms
from django.conf import settings
from django.contrib.localflavor.us.forms import USPhoneNumberField

from contact_form.forms import ContactForm
from sfmayor2011.models import AskACandidate

class ContributionsSearchForm(forms.Form):
    candidate_name = forms.CharField(max_length=255, required=False)
    contributor_name = forms.CharField(max_length=255, required=False)
    occupation = forms.CharField(max_length=255, required=False)
    employer = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=255, required=False)
    state = forms.CharField(max_length=255, required=False)
    date_from = forms.DateField(initial='01/01/2005', widget=forms.DateInput(format="%m/%d/%Y", attrs={'class': 'from'}), required=False)
    date_to = forms.DateField(initial='12/31/2009', widget=forms.DateInput(format="%m/%d/%Y", attrs={'class': 'to'}), required=False)
    amount = forms.DecimalField(required=False)

class AskACandidateForm(forms.ModelForm):
    class Meta:
        model = AskACandidate

class ReportElectionProblemsForm(ContactForm):
    body = forms.CharField(widget=forms.Textarea(), label=u'Your report')
    location = forms.CharField(max_length=255, label=u'Location')
    phone = USPhoneNumberField(label=u'Phone Number', required=False)
    time = forms.CharField(max_length=255, label=u'Time of problem', required=False)


    recipient_list = [mail_tuple[1] for mail_tuple in settings.ELECTION_REPORTS_RECIPIENTS]

    subject_template_name = "sfmayor2011/sfmayor2011_report_election_problems_subject.txt"
    
    template_name = 'sfmayor2011/sfmayor2011_report_election_problems.txt'
