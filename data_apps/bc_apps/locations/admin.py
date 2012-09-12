from django.contrib import admin

from data_apps.bc_apps.locations.models import State, County, City, Neighborhood, Coordinates

class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']    
admin.site.register(State, StateAdmin)

class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'twitter_list_name', 'twitter_user', 'twitter_list_id']    
admin.site.register(County, CountyAdmin)

class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug',]    
admin.site.register(City, CityAdmin)

class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug',]    
admin.site.register(Neighborhood, NeighborhoodAdmin)

class CoordinatesAdmin(admin.ModelAdmin):
    list_display = ['latitude', 'longitude', 'neighborhood', 'city', 'state', 'notes', 'search_query',]    
admin.site.register(Coordinates, CoordinatesAdmin)