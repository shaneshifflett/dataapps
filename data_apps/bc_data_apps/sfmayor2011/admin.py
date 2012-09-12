from django.conf import settings
from django.contrib import admin
from django import forms
from sfmayor2011.models import Candidate, Entity, Name, Place, Poll, PollRanking


class PollAdminForm(forms.ModelForm):
    class Meta:
        model = Poll

class PollRankingAdminForm(forms.ModelForm):
    class Meta:
        model = PollRanking

class CandidateAdminForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'largeTE',}), required=False)
    class Meta:
        model = Candidate

class EntityAdminForm(forms.ModelForm):
    class Meta:
        model = Entity

class NameAdminForm(forms.ModelForm):
    class Meta:
        model = Name

class PlaceAdminForm(forms.ModelForm):
    class Meta:
        model = Place

class PollAdmin(admin.ModelAdmin):
    form = PollAdminForm
    raw_id_fields = ('source', )
    list_filter = ('source__full_name__name', )

class PollRankingAdmin(admin.ModelAdmin):
    form = PollRankingAdminForm
    raw_id_fields = ('candidate', 'poll', )
    list_filter = ('candidate__entity__full_name__name', 'id',)

class CandidateAdmin(admin.ModelAdmin):
    form = CandidateAdminForm
    raw_id_fields = ('entity', 'photo', 'bio_photo')
    list_filter = ('entity__full_name__name', )
    class Media:
        js = (
            '%sjs/tiny_mce/jscripts/tiny_mce/tiny_mce.js' % '/public/',
            '%sjs/textarea.js' % '/public/',
        )

class EntityAdmin(admin.ModelAdmin):
    form = EntityAdminForm
    raw_id_fields = ('full_name', )
    list_filter = ('full_name__name', )

class NameAdmin(admin.ModelAdmin):
    form = NameAdminForm
    list_display = ('name', 'slug')
    list_filter = ('name', )

class PlaceAdmin(admin.ModelAdmin):
    form = PlaceAdminForm

admin.site.register(Poll, PollAdmin)
admin.site.register(PollRanking, PollRankingAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Name, NameAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(Candidate, CandidateAdmin)
