from django.contrib import admin

from data_apps.bc_apps.schools.models import School, SchoolDistrict

class SchoolAdmin(admin.ModelAdmin):
    list_display    = ('name', 'type', 'district', 'city', 'county')
    search_fields   = ('name', 'district__name',)
admin.site.register(School, SchoolAdmin)

class SchoolDistrictAdmin(admin.ModelAdmin):
    list_display    = ('name',)
    search_fields   = ('name',)
admin.site.register(SchoolDistrict, SchoolDistrictAdmin)