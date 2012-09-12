from django.contrib import admin

from immunizations.models import SchoolImmunization, Pertussis, IzCountyAggregate, IzCityAggregate, IzSchoolAggregate, IzDistrictAggregate

class SchoolImmunizationAdmin(admin.ModelAdmin):
    list_display    = ('school',)
    search_fields   = ('school__name',)
admin.site.register(SchoolImmunization, SchoolImmunizationAdmin)
admin.site.register(Pertussis)

class IzCountyAggregateAdmin(admin.ModelAdmin):
    list_display   = ('county', 'enrollment', 'public_number', 'percent_public', 'private_number', 'percent_private', 'up_to_date_number', 'percent_up_to_date', 'conditional_number', 'percent_conditional', 'pbe_number', 'percent_pbe', 'pertussis_number', 'pertussis_rate')
    list_filter    = ('county',)
    search_fields  = ('county__name',)
admin.site.register(IzCountyAggregate, IzCountyAggregateAdmin)

class IzCityAggregateAdmin(admin.ModelAdmin):
    list_display   = ('city', 'enrollment', 'public_number', 'percent_public', 'private_number', 'percent_private', 'up_to_date_number', 'percent_up_to_date', 'conditional_number', 'percent_conditional', 'pbe_number', 'percent_pbe',)
    list_filter    = ('city',)
    search_fields  = ('city__name',)
admin.site.register(IzCityAggregate, IzCityAggregateAdmin)

class IzSchoolAggregateAdmin(admin.ModelAdmin):
    list_display   = ('school', 'district', 'type', 'up_to_date_number', 'percent_up_to_date', 'conditional_number', 'percent_conditional', 'pbe_number', 'percent_pbe',)
    list_filter    = ('school', 'district', 'type')
    search_fields  = ('school__name', 'district__name')
admin.site.register(IzSchoolAggregate, IzSchoolAggregateAdmin)

class IzDistrictAggregateAdmin(admin.ModelAdmin):
    list_display   = ('county', 'district', 'up_to_date_number', 'percent_up_to_date', 'conditional_number', 'percent_conditional', 'pbe_number', 'percent_pbe',)
    list_filter    = ('county', 'district',)
    search_fields  = ('county__name', 'district__name')
admin.site.register(IzDistrictAggregate, IzDistrictAggregateAdmin)