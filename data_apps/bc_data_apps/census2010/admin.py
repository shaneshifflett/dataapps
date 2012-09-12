from django.contrib import admin
from census2010.models import *
from django import forms


class CensusGeographyAdminForm(forms.ModelForm):
    class Meta:
        model = CensusGeography


class GeographyTypeAdminForm(forms.ModelForm):
    class Meta:
        model = GeographyType

class GeographyTypeAdmin(admin.ModelAdmin):
	form = GeographyTypeAdminForm

class CensusGeographyAdmin(admin.ModelAdmin):
	form = CensusGeographyAdminForm

	list_filter = ['geo_type']
	raw_id_fields = ['geo_type']

admin.site.register(CensusGeography, CensusGeographyAdmin)
admin.site.register(GeographyType, GeographyTypeAdmin)