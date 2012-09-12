import locale
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from census2010.models import CensusGeography, CensusTableRow, GeographyType

locale.setlocale(locale.LC_ALL, "")

def commaify(num):
    try:
        return locale.format('%d', num, True)
    except:
        pass

def pct_change_str(old, new):
    try:
        change = "%.1f%%" % ((new - old) / float(old) * 100)
        return "<span class=\"%s\">%s</span>" % ('down' if change.startswith('-') else 'up', change.lstrip('-'))
    except:
        return "--"

def pct_str(num, total):
    try:
        return "%.1f%%" % (float(num) / total * 100)
    except:
        return "--"

POPULATION_FIELDS = (
    ('total_white', 'White'),
    ('total_indian', 'Native'),
    ('total_two_races', '2+ Races'),
    ('total_asian', 'Asian'),
    ('total_black', 'Black'),
    ('total_islander', 'Islander'),
    ('total_population', 'Total'),
    ('total_hispanic', 'Hispanic Origin'),
)

PIE_FIELDS = (
    ('total_white', 'White'),
    ('total_asian', 'Asian'),
    ('total_black', 'Black'),
)

FT_TABLE_IDS = {
    'county': '527009',
    'place': '560689',
    'legislative_lower': '517441',
    'legislative_upper': '519617',
    'tract': '517722',
    'congressional': '517159'
}

TARGET_NUMBERS = {
    'legislative_lower': 465647,
    'legislative_upper': 931349,
    'congressional': 702905
}

def legislative_list(request, geography, template_name='census2010/census_list.html'):

    # place or county
    geo_type = get_object_or_404(GeographyType, name=geography)
    race_2010 = CensusTableRow.objects.filter(geography__geo_type=geo_type,
        table_year='2010', table_name='race').order_by('geography__display_name').select_related('geography')

    total_2010 = sum(r.total_population for r in race_2010)

    total_population = {}
    total_population['2010'] = commaify(total_2010)

    percent_population = {}
    target_num = TARGET_NUMBERS[geography]
    ### PIE CHART DATA #################

    for field, name in PIE_FIELDS:
        field_total = sum(getattr(r, field) for r in race_2010)
        percent_population[name] = pct_str(field_total, total_2010).rstrip('%')

    pie_other = 100.0 - sum(float(pct) for pct in percent_population.values())
    percent_population["Other"] = "%.1f" % pie_other

    pie_data = [[name, float(pct)] for (name, pct) in percent_population.items() if float(pct) > 0.1]
    ### BUILD DATA TABLES ##############

    tables = []

    for field, name in POPULATION_FIELDS:

        new_table = {}
        new_table['headers'] = ['Name', '2010 %s Population' % name, 'Above/Below Target']
        new_table['rows'] = []
        new_table['filter'] = field

        for row in race_2010:
            pop_2010 = getattr(row, field)
            if pop_2010 != None:
                above_o_below = target_num - pop_2010
            new_row = ["<a href=\"%s\">%s</a>" % (row.geography.get_absolute_url(),\
                row.geography.display_name), commaify(pop_2010), commaify(above_o_below)]
            new_table['rows'].append(new_row)

        tables.append(new_table)


    context = {}
    total_population['2000'] = "NA"
    context['ft_table_ids'] = FT_TABLE_IDS
    context['ft_focus_id'] = FT_TABLE_IDS[geography]
    context['geo_type'] = geography
    context['tables'] = tables
    context['total_population'] = total_population 
    context['pie_data'] = pie_data

    return render_to_response(template_name, context, context_instance=RequestContext(request))

def list(request, geography, template_name='census2010/census_list.html'):
    '''
    When we add hispanic data, we use try/except tho it rly shouldn't be
    needed because the data should match up to our race rows.
    '''

    context = {}

    # place or county
    geo_type = get_object_or_404(GeographyType, name=geography)
    race_2000 = CensusTableRow.objects.filter(geography__geo_type=geo_type,
        table_year='2000', table_name='race').order_by('geography__display_name').select_related('geography')
    race_2010 = CensusTableRow.objects.filter(geography__geo_type=geo_type,
        table_year='2010', table_name='race').order_by('geography__display_name').select_related('geography')
    hispanic_2000 = CensusTableRow.objects.filter(geography__geo_type=geo_type,
        table_year='2000', table_name='hispanic').select_related('geography')
    hispanic_2010 = CensusTableRow.objects.filter(geography__geo_type=geo_type,
        table_year='2010', table_name='hispanic').select_related('geography')
    ### MODIFY QUERIES FOR COMPARE #####

    if request.GET.get('compare'):
        county = get_object_or_404(CensusGeography, slug=request.GET.get('compare'))
        cities = county.intersecting_geos.all()

        race_2000 = race_2000.filter(geography__in=cities)
        race_2010 = race_2010.filter(geography__in=cities)
        hispanic_2000 = hispanic_2000.filter(geography__in=cities)
        hispanic_2010 = hispanic_2010.filter(geography__in=cities)

        context['county'] = county

    ### OVERRIDE HISPANIC DATA #########
    for row in race_2000:
        try:
            row.total_hispanic = next(h for h in hispanic_2000 if h.geography.id == row.geography.id).total_hispanic
        except:
            pass

    for row in race_2010:
        try:
            row.total_hispanic = next(h for h in hispanic_2010 if h.geography.id == row.geography.id).total_hispanic
        except:
            pass

    ### SUM POP. ACROSS GEOGRAPHIES ####
    total_2000 = sum(r.total_population for r in race_2000)
    total_2010 = sum(r.total_population for r in race_2010)

    total_population = {}
    total_population['2000'] = commaify(total_2000)
    total_population['2010'] = commaify(total_2010)
    total_population['pct_change'] = pct_change_str(total_2000, total_2010)

    percent_population = {}
    ### PIE CHART DATA #################
    for field, name in PIE_FIELDS:
        field_total = sum(getattr(r, field) for r in race_2010)
        percent_population[name] = pct_str(field_total, total_2010).rstrip('%')

    pie_other = 100.0 - sum(float(pct) for pct in percent_population.values())
    percent_population["Other"] = "%.1f" % pie_other

    pie_data = [[name, float(pct)] for (name, pct) in percent_population.items() if float(pct) > 0.1]

    ### BUILD DATA TABLES ##############
    tables = []

    for field, name in POPULATION_FIELDS:

        new_table = {}
        new_table['headers'] = ['Name', '2010 %s Population' % name, '2000 %s Population' % name, '2000-2010 Change']
        new_table['rows'] = []
        new_table['filter'] = field

        for row in race_2010:
            pop_2010 = getattr(row, field)
            pop_2000 = getattr(next(r for r in race_2000 if r.geography_id == row.geography_id), field)
            new_row = [
                "<a href=\"%s\">%s</a>" % (row.geography.get_absolute_url(), row.geography.display_name),
                commaify(pop_2010),
                commaify(pop_2000),
                pct_change_str(pop_2000, pop_2010)
            ]
            new_table['rows'].append(new_row)

        tables.append(new_table)

    ### BUILD CONTEXT ##################
    context['ft_table_ids'] = FT_TABLE_IDS
    context['ft_focus_id'] = FT_TABLE_IDS[geography]
    context['geo_type'] = geography
    context['tables'] = tables
    context['total_population'] = total_population
    context['pie_data'] = pie_data

    return render_to_response(template_name, context, context_instance=RequestContext(request))



def legislative_detail(request, slug, template_name='census2010/census_detail.html'):

    geography = CensusGeography.objects.select_related('intersecting_geos').get(slug=slug)

    row_2010 = CensusTableRow.objects.get(geography=geography,
        table_year='2010', table_name='race')

    hispanic_2010 = CensusTableRow.objects.get(geography=geography,
        table_year='2010', table_name='hispanic')

    try:
        row_2010.total_hispanic = hispanic_2010.total_hispanic
    except:
        pass

    ### BUILD DATA TABLE ###############

    rows = []
    headers = ['Race/ethnicity', '2010 Population', '2010 Percentage']

    for field, name in POPULATION_FIELDS:
        new_row = [
            name,
            commaify(getattr(row_2010, field)),
            pct_str(getattr(row_2010, field), row_2010.total_population),
        ]
        rows.append(new_row)

    percent_population = {}

    ### PIE CHART DATA #################

    for field, name in PIE_FIELDS:
        percent_population[name] = pct_str(getattr(row_2010, field), row_2010.total_population).rstrip('%')

    pie_other = 100.0 - sum(float(pct) for pct in percent_population.values())
    percent_population["Other"] = "%.1f" % pie_other

    pie_data = [[name, float(pct)] for (name, pct) in percent_population.items() if float(pct) > 0.1]
    ### BUILD CONTEXT ##################
    if geography.geo_type.name == 'county' or geography.geo_type.name == 'legislative_lower' or geography.geo_type.name == 'legislative_upper':
        focus_ft_id = FT_TABLE_IDS['place']
    else:
        focus_ft_id = FT_TABLE_IDS[geography.geo_type.name]

    total_population = {}
    total_population['2010'] = commaify(row_2010.total_population)
    total_population['2000'] = "NA"
    context = {}
    context['geography'] = geography
    context['geo_type'] = geography.geo_type.name
    context['focus_ft_id'] = focus_ft_id
    context['rows'] = rows
    context['headers'] = headers
    context['total_population'] = total_population
    context['pie_data'] = str(pie_data)
    context['ft_table_ids'] = FT_TABLE_IDS

    return render_to_response(template_name, context, context_instance=RequestContext(request))

def detail(request, slug, template_name='census2010/census_detail.html'):
    
    geography = get_object_or_404(CensusGeography, slug=slug)

    row_2000 = CensusTableRow.objects.get(geography=geography,
        table_year='2000', table_name='race')
    row_2010 = CensusTableRow.objects.get(geography=geography,
        table_year='2010', table_name='race')

    hispanic_2000 = CensusTableRow.objects.get(geography=geography,
        table_year='2000', table_name='hispanic')
    hispanic_2010 = CensusTableRow.objects.get(geography=geography,
        table_year='2010', table_name='hispanic')

    ### OVERRIDE HISPANIC DATA #########

    try:
        row_2000.total_hispanic = hispanic_2000.total_hispanic
    except:
        pass

    try:
        row_2010.total_hispanic = hispanic_2010.total_hispanic
    except:
        pass

    percent_population = {}

    ### PIE CHART DATA #################

    for field, name in PIE_FIELDS:
        percent_population[name] = pct_str(getattr(row_2010, field), row_2010.total_population).rstrip('%')

    pie_other = 100.0 - sum(float(pct) for pct in percent_population.values())
    percent_population["Other"] = "%.1f" % pie_other

    pie_data = [[name, float(pct)] for (name, pct) in percent_population.items() if float(pct) > 0.1]

    ### BUILD DATA TABLE ###############

    rows = []
    headers = ['Race/ethnicity', '2010 Population', '2010 Percentage', '2000 Population',
        '2000 Percentage', '2000-2010 Change']

    for field, name in POPULATION_FIELDS:
        new_row = [
            name,
            commaify(getattr(row_2010, field)),
            pct_str(getattr(row_2010, field), row_2010.total_population),
            commaify(getattr(row_2000, field)),
            pct_str(getattr(row_2000, field), row_2000.total_population),
            pct_change_str(getattr(row_2000, field), getattr(row_2010, field)),
        ]
        rows.append(new_row)

    ### BUILD CONTEXT ##################
    if geography.geo_type.name == 'county':
        focus_ft_id = FT_TABLE_IDS['place']
    else:
        focus_ft_id = FT_TABLE_IDS[geography.geo_type.name]

    total_population = {}
    total_population['2000'] = commaify(row_2000.total_population)
    total_population['2010'] = commaify(row_2010.total_population)
    total_population['pct_change'] = pct_change_str(row_2000.total_population, row_2010.total_population)
    context = {}
    context['geography'] = geography
    context['geo_type'] = geography.geo_type.name
    context['focus_ft_id'] = focus_ft_id
    context['rows'] = rows
    context['headers'] = headers
    context['total_population'] = total_population
    context['pie_data'] = str(pie_data)
    context['ft_table_ids'] = FT_TABLE_IDS

    return render_to_response(template_name, context, context_instance=RequestContext(request))
