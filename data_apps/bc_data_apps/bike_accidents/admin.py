from django.conf import settings
from django.contrib import admin

from data_apps.bc_data_apps.bike_accidents.forms import ViolationCodeAdminForm
from data_apps.bc_data_apps.bike_accidents.models import BikeAccident, SubmittedBikeAccident, ViolationCode

class ViolationCodeAdmin(admin.ModelAdmin):
    form = ViolationCodeAdminForm

admin.site.register(ViolationCode, ViolationCodeAdmin)
    
class BikeAccidentAdmin(admin.ModelAdmin):
    date_hierarchy = 'happened_at'
    list_display   = ('case_number', 'happened_at', 'violation_code', 'primary_street', 'cross_street', 'vehicle_one', 
                      'vehicle_two', 'vehicle_three', 'number_injured', 'fatalities', 'hit_and_run')
    list_filter    = ('violation_code', 'primary_street', 'cross_street', 'vehicle_one', 'vehicle_two', 'vehicle_three', 'hit_and_run')
    search_fields  = ('violation_code__title', 'primary_street__name', 'cross_street__name', 'vehicle_one__name', 'vehicle_two__name', 'vehicle_three__name',)    
admin.site.register(BikeAccident, BikeAccidentAdmin)
    
