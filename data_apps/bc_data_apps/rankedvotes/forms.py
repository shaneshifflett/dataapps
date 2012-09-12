from django import forms
from data_apps.bc_data_apps.rankedvotes.models import RankedBallot

class RankedBallotForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self,).__init__(*args, **kwargs)
        if 'first_choice' in self.initial.keys():
            options = self.initial['first_choice']
            self.fields['first_choice'] = forms.ChoiceField(choices=options, label='First Choice')
            self.fields['second_choice'] = forms.ChoiceField(choices=options, label='Second Choice')
            self.fields['third_choice'] = forms.ChoiceField(choices=options, label='Third Choice')
