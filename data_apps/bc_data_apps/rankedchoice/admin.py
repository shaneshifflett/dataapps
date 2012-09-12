from django.conf import settings
from django.contrib import admin
from data_apps.bc_data_apps.rankedchoice.models import *

class RoundAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'admin/js/calendar.js',
            'admin/js/admin/DateTimeShortcuts.js',
            '%sjs/tiny_mce/jscripts/tiny_mce/tiny_mce.js' % '/public/',
            '%sjs/textarea_all.js' % '/public/',
        )

admin.site.register(RankedChoiceRound, RoundAdmin)
admin.site.register(CandidateRoundRank)


