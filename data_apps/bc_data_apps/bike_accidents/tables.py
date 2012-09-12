import django_tables as tables

from data_apps.bc_data_apps.bike_accidents.models import BikeAccident

class BikeAccidentTable(tables.ModelTable):
    date            = tables.Column(data='happened_at')
    street1         = tables.Column(data='primary_street__name') 
    street2         = tables.Column(data='cross_street__name') 
    at_fault        = tables.Column(data='vehicle_one')
    second_vehicle  = tables.Column(data='vehicle_two')
    fatalities      = tables.Column(data='fatalities')
    violation_category   = tables.Column(data='violation_code__code')
    hit_and_run     = tables.Column(data='hit_and_run')
    county          = tables.Column(data='county')
    city            = tables.Column(data='city')
    lighting        = tables.Column(data='lighting')
    road_surface    = tables.Column(data='road_surface')
    injured         = tables.Column(data='injured')
