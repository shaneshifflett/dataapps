
from django.conf import settings
from django.contrib import admin
from data_apps.bc_data_apps.rankedvotes.models import *


class RaceAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'admin/js/calendar.js',
            'admin/js/admin/DateTimeShortcuts.js',
            '%sjs/tiny_mce/jscripts/tiny_mce/tiny_mce.js' % '/public/',
            '%sjs/textarea_all.js' % '/public/',
        )
    exclude = ('votes',)

admin.site.register(Race, RaceAdmin)
admin.site.register(Candidate)

class RankedBallotAdmin(admin.ModelAdmin):
    list_display =  ('id', 'choice_one', 'choice_two', 'choice_three',)
admin.site.register(RankedBallot, RankedBallotAdmin)


