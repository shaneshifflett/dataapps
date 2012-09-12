from django import forms
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
#few mods to the FormWizard class to avoid modifying Django


class RawDataForm(forms.Form):
    RUSH_HOUR_CHOICES = (
        ('alltimes','All Times'),
        ('morning','Morning Commute [7-10am]'),
        ('afternoon','Evening Commute [4-7pm]'),
    )
    ACCIDENT_TYPE_CHOICES = (
        ('alltypes','All Types'),
        ('hitandrun','Just Hit and Runs'),
        ('fatal','Just Fatalities'),
    )
    AT_FAULT_CHOICES = (
        ('allfaults', 'All Faults'),
        ('BICYCLIST', 'Just Bikes'),
        ('AUTO', 'Just Cars'),
        ('PARKED_AUTO', 'Parked Cars'),
        ('PEDESTRIAN', 'Just Pedestrians'),
        ('NO_FAULT', 'No fault'),
        ('SOLO_ACCIDENT', 'Solo accident'),
        ('OTHER', 'Other (see analysis)')
    )
    VIOLATION_CHOICES = (
        ('allcitations', 'All violations'),
        ('10', 'NA'),
        ('5', 'Automobile right of way'),
        ('21', 'Brakes'),
        ('9', 'Driving/Biking under the influence'),
        ('8', 'Following too closely'),
        ('22', 'Hazardous parking'),
        ('20', 'Impeding traffic'),
        ('15', 'Improper passing'),
        ('2', 'Improper turning'),
        ('19', 'Lights'),
        ('18', 'Other equipment'),
        ('11', 'Other hazardous violation'),
        ('14', 'Other improper driving'),
        ('12', 'Other than driver'),
        ('16', 'Pedestrian right of way'),
        ('6', 'Pedestrian violation'),
        ('7', 'Traffic signals and signs'),
        ('4', 'Unknown'),
        ('13', 'Unsafe lane change'),
        ('1', 'Unsafe speed'),
        ('17', 'Unsafe starting or breaking'),
        ('3', 'Wrong side of road')
    )
    
    LIGHTING_CHOICES = (
        ('anylighting', 'Any lighting'),
        ('1', 'Daylight'),
        ('2', 'Dark - street lights'),
        ('5', 'Dark - no lights'),
        ('6', 'Dark - broken lights'),
        ('3', 'Dusk/dawn'),
        ('4', 'NA')
    )

    ROAD_CHOICES = (
        ('allconditions', 'All conditions'),
        ('1', 'Dry'),
        ('2', 'Wet'),
        ('4', 'Slippery'),
        ('5', 'Snow or ice'),
        ('3', 'NA')
    )

    COUNTY_CHOICES = (
        ('allcounties', 'All counties'),
        ('5', 'Alameda'),
        ('1', 'Contra Costa'),
        ('3', 'Marin'),
        ('7', 'Napa'),
        ('87', 'San Francisco'),
        ('12', 'San Mateo'),
        ('8', 'Santa Clara'),
        ('16', 'Solano'),
        ('25', 'Sonoma')
    )

    ACCIDENT_SOURCE = (
        ('0', 'Official CHP Data'),
        ('1', 'User Submitted Accidents')
    )
    date_from = forms.DateField(initial='01/01/2005', widget=forms.DateInput(format="%m/%d/%Y", attrs={'class': 'from'}), required=False)
    date_to = forms.DateField(initial='12/31/2009', widget=forms.DateInput(format="%m/%d/%Y", attrs={'class': 'to'}), required=False)
    accident_type = forms.ChoiceField(choices=ACCIDENT_TYPE_CHOICES, required=False)
    at_fault = forms.ChoiceField(choices=AT_FAULT_CHOICES, required=False)
    violation = forms.ChoiceField(choices=VIOLATION_CHOICES, required=False)
    lighting = forms.ChoiceField(choices=LIGHTING_CHOICES, required=False)
    road_condition = forms.ChoiceField(choices=ROAD_CHOICES, required=False)
    county = forms.ChoiceField(choices=COUNTY_CHOICES, required=False)
    accident_source = forms.ChoiceField(choices=ACCIDENT_SOURCE, required=False)

'''
class SubmittedAccidentsWizard(FormWizard):
    def process_step(self, request, form, step):
        if step == 0:
            obj = form.save()
            self.extra_context['accidente'] = obj
        elif step == 1:
            obj = self.extra_context['accidente']
            obj.number_injured = form.cleaned_data['number_injured']
            obj.fatalities = form.cleaned_data['fatalities']
            obj.accident_cause = form.cleaned_data['accident_cause']
            obj.save()
            self.extra_context['accidente'] = obj
        elif step == 2:
            obj = self.extra_context['accidente']
            obj.injury_description = form.cleaned_data['injury_description']
            obj.officially_reported = form.cleaned_data['officially_reported']
            obj.next_steps = form.cleaned_data['next_steps']
            obj.accident_cost = form.cleaned_data['accident_cost']
            obj.cost_description = form.cleaned_data['cost_description']
            obj.save()

    def get_template(self, step):
        return ['bike_accidents/bike_accidents_report_%s.html' % step, 'bike_accidents/bike_accidents_report.html']

    def done(self, request, form_list):
        return HttpResponseRedirect(reverse('bike_accidents_thanks'))

class SubmittedBikeAccidentFormThree(forms.ModelForm):
    class Meta:
        model = SubmittedBikeAccident
        fields = (
            'injury_description',
            'officially_reported',
            'next_steps',
            'accident_cost',
            'cost_description')

class SubmittedBikeAccidentFormTwo(forms.ModelForm):
    class Meta:
        model = SubmittedBikeAccident
        fields = (
            'number_injured',
            'fatalities',
            'hit_and_run',
            'accident_cause')

        widgets = {
            'hit_and_run':forms.RadioSelect()
        }
   
class SubmittedBikeAccidentFormOne(forms.ModelForm):
    class Meta:
        model = SubmittedBikeAccident
        fields = (
            'name',
            'phone',
            'email',
            'age',
            'date',
            'hour',
            'minute',
            'ampm',
            'primary_street',
            'cross_street',
            'city',
            'zip_code',
            'follow_up',
            'description')

        widgets = {
            'follow_up': forms.RadioSelect(),
            'ampm': forms.RadioSelect(),
            'description': forms.Textarea(attrs={'cols': 10, 'rows': 20})
        }
'''
