from django.core.exceptions import ObjectDoesNotExist
from csv import reader, writer
from google import ftclient
from google.authorization.clientlogin import ClientLogin
from models import *
import utils
import views
import re
"""
instructions for loading data
NOTE: you have to d/l the 2010 from http://www2.census.gov/census_2010/01-Redistricting_File--PL_94-171/
NOTE: change the file paths below to point to your local data
NOTE: for test data, change any of the 'ca' strings to 'il'

in citizen root ./manage.py shell
from census2010 import data_loaders
data_loaders.populate_geo_types()
data_loaders.populate_logrec_mappings(data_loaders.ca_geo_path)
data_loaders.ca_2000_data()
data_loaders.load_2010_data('race', data_loaders.map_row_race, '06')
data_loaders.load_2010_data('hispanic', data_loaders.map_row_hispanic, '06')

"""

il_file_path = '/Users/shaneshifflett/Documents/work/baycitizen/census/il2010.pl/' 
il_geo_path = il_file_path + 'ilgeo2010.pl'
s_one_path = il_file_path + 'il000012010.pl'
s_two_path = il_file_path + 'il000022010.pl'

ca_file_path = '/Users/shaneshifflett/dev/ca2010.pl/'
ca_geo_path = ca_file_path + 'cageo2010.pl'
ca_one_path = ca_file_path + 'ca000012010.pl'
ca_two_path = ca_file_path + 'ca000022010.pl'
#dictionary mapping column headers to their start end position
#geofiles key to index
gfki = {
    'fileid': list([0,5]),
    'stusab': list([6,8]),
    'sumlev': list([8,11]),
    'geocomp': list([11,13]),
    'chariter': list([13,16]),
    'cifsn': list([16,18]),
    'logrecno': list([18,25]),
    'region': list([25,26]),
    'division': list([26,27]),
    'state': list([27,29]),
    'county': list([29,32]),
    'countycc': list([32,34]),
    'countysc': list([34,36]),
    'cousub': list([36,41]),
    'cousubcc': list([41,43]),
    'cousubsc': list([43,45]),
    'place': list([45,50]),
    'placecc': list([50,52]),
    'placesc': list([52,54]),
    'tract': list([54,60]),
    'blkgrp': list([60,61]),
    'block': list([61,65]),
    'iuc': list([65,67]),
    'congressional': list([153,155]),
    'state_leg_upper': list([155,158]),
    'state_leg_lower': list([158,161]),
    'name': list([226,316]),
    'funcstat': list([316,317]),
    'gcuni': list([317,318]),
    'pop100': list([318,327]),
    'hu100': list([327,336]),
    'intplat': list([336,347]),
    'intptlon': list([347,359]),
    'lsadc': list([359,361]),
    'partflag': list([361,326])
}
#list of table names associated with the file name and a range for columns occupied
il_table_keys = {
    'race': [s_one_path, 5, 75],
    'hispanic': [s_one_path, 76, 148],
    '18_plus_race': [s_two_path, 5, 75],
    '18_place_hispanic': [s_two_path, 76, 148]
}

ca_table_keys = {
    'race': [ca_one_path, 5, 75],
    'hispanic': [ca_one_path, 76, 148],
    '18_plus_race': [ca_two_path, 5, 75],
    '18_place_hispanic': [ca_two_path, 76, 148]
}
#column names and index for each column
table_one_three_keys = {
    'total': 0,
    'total_one_race': 1,
    'white_one_race': 2,
    'black_one_race': 3,
    'indian_one_race': 4,
    'asian_one_race': 5,
    'islander_one_race': 6,
    'other_one_race': 7,
    'two_races': 8,
    'population_two_races': 9,
}

#hispanic or latino, not by race
table_two_four_keys = {
    'total': 0,
    'total_hispanic': 1,
    'total_not_hispanic': 2,
    'not_hispanic_one_race': 3,
    'not_hispanic_one_race_white': 4,
    'not_hispanic_one_race_black': 5,
    'not_hispanic_one_race_indian': 6,
    'not_hispanic_one_race_asian': 7,
    'not_hispanic_one_race_islander': 8,
    'not_hispanic_one_race_other': 9
}



lr_to_gf = {} #logical records associated with an entry in the geo file

def get_geo_column(col_name, row):
    return row[gfki[col_name][0]:gfki[col_name][1]]

def read_table(f_directory):
    """
    f_directory: an entry from table_keys to get necessary file and column information
    data_hole: a dictionary to populate 
    """
    data_hole = {}
    for idx, row in enumerate(reader(open(f_directory[0], 'rb'))):
        logrecno = row[4]
        data_hole[logrecno] = row[f_directory[1]:f_directory[2]]
    return data_hole

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

def populate_logrec_mappings(this_file_path):
    """
    should read in the global var to the geo path
    as of 3/7/2010 it's ca_geo_path or il_geo_path
    """
    for row in reader(open(this_file_path, 'rb')):
        key = get_geo_column('logrecno', row[0])
        t_sumlvl = get_geo_column('sumlev', row[0])
        t_state = get_geo_column('state', row[0])
        t_county = get_geo_column('county', row[0])
        t_place = get_geo_column('place', row[0])
        t_legis_upper = get_geo_column('state_leg_upper', row[0])
        t_legis_lower = get_geo_column('state_leg_lower', row[0])
        t_name = get_geo_column('name', row[0])
        t_congressional = get_geo_column('congressional', row[0])
        t_tract = get_geo_column('tract', row[0])
        if t_name.find("\xF1") > 0:
            print "special character %s" % t_name
            t_name = t_name.replace("\xF1", "n")
        GeoFileMapping(logrecno=key, state_code=t_state, county_code=t_county,\
        place_code=t_place, state_legislative_upper_code=t_legis_upper, \
        state_legislative_lower_code=t_legis_lower, name=t_name,\
        summary_level=t_sumlvl, congressional_code=t_congressional,\
        tract_code=t_tract).save()

def populate_geo_types():
    GeographyType(name='county').save()
    GeographyType(name='place').save()
    GeographyType(name='legislative_upper').save()
    GeographyType(name='legislative_lower').save()
    GeographyType(name='congressional').save()
    GeographyType(name='tract').save()

summary_levels = {
    'county': '050',
    'place': '160',
    'legislative_lower': '620',
    'legislative_upper': '610',
    'congressional': '500',
    'tract': '140'
}

def map_row_race(row, geo, year, table_name):
    ct_row = CensusTableRow(geography=geo, total_population=row[0], total_population_one_race=row[1],\
                total_white=row[2], total_black=row[3], total_indian=row[4], total_asian=row[5], \
                total_islander=row[6], total_other=row[7], total_two_races=row[8], total_population_two_races=row[9],\
                table_name=table_name, table_year=year)
    ct_row.save()

def map_row_hispanic(row, geo, year, table_name):
    ct_row = CensusTableRow(geography=geo, total_population=row[0], total_population_one_race=row[3],\
            total_white=row[4], total_black=row[5], total_indian=row[6], total_asian=row[7], \
            total_islander=row[8], total_other=row[9], total_hispanic=row[1], total_not_hispanic=row[2],\
            table_name=table_name, table_year=year)
    ct_row.save()

def census_obj_lookups(lookup_func, geo_id, logrecno, geo_type, table_name):
    try:
        lookup_func()
    except ObjectDoesNotExist as e:
        print "SUBGEOS: EXCPETIONS geo_id=%s logrecno=%s geotype=%s table_name=%s e=%s" % \
        (geo_id, logrecno, geo_type, table_name, e)
    except Exception as e:
        print "SUBGEOS: EXCEPTIONS_e=%s" % e


def intersect_congressional():
    places = CensusGeography.objects.filter(geo_type__name='place')
    for p in places:
        try:
            code = p.geo_id.split('06', 1)[1]
            #find the counties that intersect a place
            mapping_file_relations = GeoFileMapping.objects.filter(place_code=code, summary_level='531')
            for mfr in mapping_file_relations:
                print "SUBGEOS_COUNTY: place_code=%s congressional_code=%s\
                name=%s" % (code, mfr.congressional_code, mfr.name)
                congress = CensusGeography.objects.get(geo_id='06'+mfr.congressional_code, \
                geo_type__name='congressional')
                congress.intersecting_geos.add(p)

        except ObjectDoesNotExist as e:
            print "SUBGEOS: EXCPETIONS code=%s e=%s" % \
            (code, e)
        except Exception as e:
            print "SUBGEOS: EXCEPTIONS_e=%s" % e

def load_2010_data(table_name, mapping_func, state_code, geo_type_name='all'):
    #we'll get the mappings from geo file header to look up the logrec#
    #and pull out the row for a particular table in the 2010 census summary files
    if state_code == '17':
        table_one = read_table(il_table_keys[table_name])
    elif state_code == '06':
        table_one = read_table(ca_table_keys[table_name])
    if geo_type_name == 'all':
        geo_types = GeographyType.objects.all()
    else:
        geo_types = GeographyType.objects.filter(name=geo_type_name)
    for geotype in geo_types:
        geos = CensusGeography.objects.filter(geo_type=geotype)
        for item in geos:
            try:
                logrecno = None
                code = item.geo_id.split(state_code, 1)[1]
                if geotype.name == 'county':
                    geo_mapping = GeoFileMapping.objects.get(county_code=code,\
                    summary_level=summary_levels[geotype.name])
                elif geotype.name == 'place':
                    geo_mapping = GeoFileMapping.objects.get(place_code=code,\
                    summary_level=summary_levels[geotype.name])
                elif geotype.name == 'legislative_upper':
                    geo_mapping = GeoFileMapping.objects.get(state_legislative_upper_code=code, \
                    summary_level=summary_levels[geotype.name])
                elif geotype.name == 'legislative_lower':
                    geo_mapping = GeoFileMapping.objects.get(state_legislative_lower_code=code, \
                    summary_level=summary_levels[geotype.name])
                elif geotype.name == 'congressional':
                    geo_mapping = GeoFileMapping.objects.get(congressional_code=\
                    code, summary_level=summary_levels[geotype.name])
                logrecno = geo_mapping.logrecno

                row = table_one[logrecno]
                mapping_func(row, item, '2010', table_name)

                if geotype.name == 'place':
                    def sub_counties():
                        #find the counties that intersect a place
                        mapping_file_relations = GeoFileMapping.objects.filter(place_code=code, summary_level='155')
                        for mfr in mapping_file_relations:
                            print "SUBGEOS_COUNTY: place_code=%s county_code=%s\
                            name=%s" % (code, mfr.county_code, mfr.name)
                            county = CensusGeography.objects.get(geo_id=mfr.state_code+mfr.county_code, \
                            geo_type__name='county')
                            county.intersecting_geos.add(item)
                    census_obj_lookups(sub_counties, item.geo_id, logrecno, geotype.name, table_name)

                    def sub_upper_legis():
                        #find the upper legislative districts that intersect a place
                        mapping_file_relations = GeoFileMapping.objects.filter(place_code=code, \
                        summary_level='642')
                        for mfr in mapping_file_relations:
                            print "SUBGEOS_UPPERLEGIS: place_code=%s luc=%s \
                            name=%s" % (code, mfr.state_legislative_upper_code, mfr.name)
                            legis_upper = CensusGeography.objects.get(\
                            geo_id=mfr.state_code+mfr.state_legislative_upper_code,\
                            geo_type__name='legislative_upper')
                            legis_upper.intersecting_geos.add(item)
                    census_obj_lookups(sub_upper_legis, item.geo_id, logrecno, geotype.name, table_name)

                    def sub_lower_legis():
                        #find the lower legislative districts that intersect a place
                        mapping_file_relations = GeoFileMapping.objects.filter(place_code=code, \
                        summary_level='643')
                        for mfr in mapping_file_relations:
                            print "SUBGEOS_LOWERLEGIS: place_code=%s llc=%s\
                             name=%s" % (code, mfr.state_legislative_lower_code, mfr.name)
                            legis_lower = CensusGeography.objects.get(\
                            geo_id=mfr.state_code+mfr.state_legislative_lower_code,\
                            geo_type__name='legislative_lower')
                            legis_lower.intersecting_geos.add(item)
                    census_obj_lookups(sub_lower_legis, item.geo_id, logrecno, geotype.name, table_name)

            except ObjectDoesNotExist as e:
                print "GEOS: EXCPETIONS geo_id=%s logrecno=%s geotype=%s table_name=%s e=%s" % \
                (item.geo_id, logrecno, geotype.name, table_name, e)
            except Exception as e:
                print "GEOS: EXCEPTIONS_e=%s" % e


def del_tract_intersections():
    geos = CensusGeography.objects.all()
    for geo in geos:
        tracts = geo.intersecting_geos.filter(geo_type__name='tract')
        for t in tracts:
            geo.intersecting_geos.remove(t)

def filter_ca_tracts():
    """
    See ca_2000_tracts()
    """
    tracts = CensusGeography.objects.filter(geo_type__name='tract')
    for tract in tracts:
        county_id = tract.geo_id[0:5]
        try:
            county = CensusGeography.objects.get(geo_id=county_id, geo_type__name='county')
        except:
            tract.delete()

def intersect_tracts_ca():
    """
    find all geographies that intersect a tract and save the info
    intersections are found by looking at the summary level and an id for that geography type
    geo_type_name   |   summary_level
    legislative_lower = 636
    legislative_upper = 631
    congressional = 511
    county = 140 
    """
    tracts = CensusGeography.objects.filter(geo_type__name='tract')
    for t in tracts:
        """
        code = t.geo_id[2:5]
        mfrs = GeoFileMapping.objects.filter(tract_code=t.geo_id[5:], summary_level='636')
        if len(mfrs) > 0:
            try:
                ll = CensusGeography.objects.get(geo_id='06'+mfrs[0].state_legislative_lower_code,\
                geo_type__name='legislative_lower')
                ll.intersecting_geos.add(t)
            except Exception as e:
                print 'e=%s tract=%s' % (e, t.geo_id)
        mfrs = GeoFileMapping.objects.filter(tract_code=t.geo_id[5:], summary_level='631')
        if len(mfrs) > 0:
            try:
                lu = CensusGeography.objects.get(geo_id='06'+mfrs[0].state_legislative_upper_code,geo_type__name=\
                'legislative_upper')
                lu.intersecting_geos.add(t)
            except Exception as e:
                print 'e=%s tract=%s' % (e, t.geo_id)
        mfrs = GeoFileMapping.objects.filter(tract_code=t.geo_id[5:], summary_level='511')
        if len(mfrs) > 0:
            try:
                c = CensusGeography.objects.get(geo_id='06'+mfrs[0].congressional_code, geo_type__name='congressional')
                c.intersecting_geos.add(t)
            except Exception as e:
                print 'e=%s tract=%s' % (e, t.geo_id)
        """
        mfrs = GeoFileMapping.objects.filter(tract_code=t.geo_id[5:], summary_level='140')
        if len(mfrs) > 0:
            try:
                c = CensusGeography.objects.get(geo_id='06'+mfrs[0].county_code,geo_type__name='county')
                c.intersecting_geos.add(t)
            except Exception as e:
                print 'e=%s tract=%s' % (e, t.geo_id)

def write_tract_county():
    counties = CensusGeography.objects.filter(geo_type__name='county')
    m_writer = writer(open('tract_county.csv', 'wb'), delimiter=',')
    m_writer.writerow(['tract geoid', 'county geoid'])
    for c in counties:
        for t in c.intersecting_geos.filter(geo_type__name='tract'):
            m_writer.writerow([t.geo_id, c.geo_id])

def print_ca_geos(geo_type):
    m_writer = writer(open('geo_listing.csv', 'wb'), delimiter=',')
    fields = ['tract_name', '2000_total_population',\
    '2010_total_population', 'pct_change_total_population', '2000_total_white',\
    '2010_total_white', 'pct_change_total_white', '2000_total_black',\
    '2010_total_black', 'pct_change_total_black', '2000_total_indian',\
    '2010_total_indian', 'pct_change_total_indian', '2000_total_asian',\
    '2010_total_asian', 'pct_change_total_asian', '2000_total_islander',\
    '2010_total_islander', 'pct_change_total_islander', '2000_total_other',\
    '2010_total_other', 'pct_change_total_other', '2000_total_population_one_race',\
    '2010_total_population_one_race', 'pct_change_total_population_one_race',\
    '2000_total_two_races', '2010_total_two_races', 'pct_change_total_two_races',\
    '2000_total_hispanic', '2010_total_hispanic', 'pct_change_total_hispanic']
    m_writer.writerow(fields)
    tracts = CensusGeography.objects.filter(geo_type__name=geo_type)
    for t in tracts:
        myrow = list()
        myrow.append(t.display_name)
        i = 0
        while i + 2 < len(fields):
            field_name = re.split('(\d_?)|(pct_change_)', fields[i+1])
            old_row = CensusTableRow.objects.get(table_name='hispanic',\
            table_year='2000', geography=t)
            old_data = getattr(old_row, field_name[len(field_name)-1])
            myrow.append(old_data)

            field_name = re.split('(\d_?)|(pct_change_)', fields[i+2])
            new_row = CensusTableRow.objects.get(table_name='hispanic',\
            table_year='2010', geography=t)
            new_data = getattr(new_row, field_name[len(field_name)-1])
            myrow.append(new_data)

            pct_change = utils.pct_change(old_data, new_data)
            myrow.append(pct_change)
            i = i + 3
            
        m_writer.writerow(myrow)

def ca_2000_tracts():
    """
    loads in the USA tract data for 2000 and 2010 cenus summary files
    this is ALL ca tracts and we need to run filter_ca_tracts to reduce
    the CA TRACTS to include only those in the bay area
    """
    file_name = 'dataapps/census2010/data/TractCA.csv'
    rows = list(reader(open(file_name, 'rb')))
    for row in rows[2:]:
        state_code = "0"+row[9]
        try:
            geo = CensusGeography.objects.get(geo_id="0"+row[399])
        except:
            geo = CensusGeography(geo_id="0"+row[399],\
            display_name=row[65], info_text='derp')

            geo.geo_type = GeographyType.objects.get(name='tract')
            geo.save()

        total_population_2000 = row[425]
        total_white_2000 = row[429]
        total_black_2000 = row[432]
        total_indian_2000 = row[435]
        total_asian_2000 = row[438]
        total_islander_2000 = row[441]
        total_other_2000 = row[444]
        total_two_races_2000 = row[447]
        total_hispanic_2000 = row[450]
        total_not_hispanic_2000 = row[453]

        total_one_race_2000 = int(total_white_2000) + int(total_black_2000) +\
        int(total_indian_2000) + int(total_asian_2000) + int(total_islander_2000) +\
        int(total_other_2000)

        total_population_2010 = row[101]
        total_one_race_2010 = row[102]
        total_white_2010 = row[103]
        total_black_2010 = row[104]
        total_indian_2010 = row[105]
        total_asian_2010 = row[106]
        total_islander_2010 = row[107]
        total_other_2010 = row[108]
        total_two_races_2010 = row[109]
        total_hispanic_2010 = row[173]
        total_not_hispanic_2010 = row[174]


        ct_row = CensusTableRow(geography=geo,
        total_population=total_population_2000,\
        total_population_one_race=total_one_race_2000,\
        total_white=total_white_2000, total_black=total_black_2000,\
        total_indian=total_indian_2000, total_asian=total_asian_2000,\
        total_islander=total_islander_2000, total_other=total_other_2000,\
        total_two_races=total_two_races_2000, table_name='race', table_year='2000')
        ct_row.save()


        ct_row = CensusTableRow(geography=geo,
        total_population=total_population_2000,\
        total_population_one_race=total_one_race_2000,\
        total_white=total_white_2000, total_black=total_black_2000,\
        total_indian=total_indian_2000, total_asian=total_asian_2000,\
        total_islander=total_islander_2000, total_other=total_other_2000,\
        total_two_races=total_two_races_2000, total_hispanic=total_hispanic_2000,\
        table_name='hispanic', table_year='2000')
        ct_row.save()

        ct_row = CensusTableRow(geography=geo,
        total_population=total_population_2010,\
        total_population_one_race=total_one_race_2010,\
        total_white=total_white_2010, total_black=total_black_2010,\
        total_indian=total_indian_2010, total_asian=total_asian_2010,\
        total_islander=total_islander_2010, total_other=total_other_2010,\
        total_two_races=total_two_races_2010, table_name='race', table_year='2010')
        ct_row.save()


        ct_row = CensusTableRow(geography=geo,
        total_population=total_population_2010,\
        total_population_one_race=total_one_race_2010,\
        total_white=total_white_2010, total_black=total_black_2010,\
        total_indian=total_indian_2010, total_asian=total_asian_2010,\
        total_islander=total_islander_2010, total_other=total_other_2010,\
        total_two_races=total_two_races_2010, total_hispanic=total_hispanic_2010,\
        table_name='hispanic', table_year='2010')
        ct_row.save()


def ca_2000_data():
    ca_files = {
    'dataapps/census2010/data/ca_2000_all_counties.csv': 'county',
    'dataapps/census2010/data/ca_2000_all_cities.csv':'place',
    'dataapps/census2010/data/ca_2000_upper_legislative.csv':'legislative_upper',
    'dataapps/census2010/data/ca_2000_lower_legislative.csv':'legislative_lower',
    'dataapps/census2010/data/ca_2000_all_congressional.csv':'congressional'
    }
    for k, v in ca_files.items():
        rows = list(reader(open(k, 'rb')))
        for row in rows[1:]:
            try:
                geo = CensusGeography.objects.get(geo_id=row[1], geo_type__name=v)
            except:
                geo = CensusGeography(geo_id=row[1], display_name=row[3], info_text='derp')
                geo.geo_type = GeographyType.objects.get(name=v)
                geo.save()
            #add the race row for a geo
            print row
            ct_row = CensusTableRow(geography=geo, total_population=row[4], total_population_one_race=row[5],\
            total_white=row[6], total_black=row[7], total_indian=row[8], total_asian=row[9], \
            total_islander=row[10], total_other=row[11], total_two_races=row[12],\
            table_name='race', table_year='2000')
            ct_row.save()
            #add the hispanic row for a geo, the files retrieved have both hispanic and race data in them
            #so it looks like we are just duplicating values but in more robust files the values assigned
            #to all properties may differ between a hispanic table and a race table
            ct_row = CensusTableRow(geography=geo, total_population=row[4], total_population_one_race=row[5],\
            total_white=row[6], total_black=row[7], total_indian=row[8], total_asian=row[9], \
            total_islander=row[10], total_other=row[11], total_two_races=row[12], total_hispanic=row[13], \
            table_name='hispanic', table_year='2000')
            ct_row.save()

def il_2000_data():
    race_files = {'dataapps/census2010/data/il_sample_2000_county_race.csv':'county',
    'dataapps/census2010/data/il_sample_2000_city_race.csv':'place',
    'dataapps/census2010/data/il_sample_2000_legislative_upper_race.csv':'legislative_upper'
    }
    for k, v in race_files.items():
        for row in reader(open(k, 'rb')):
            try:
                geo = CensusGeography.objects.get(geo_id=row[1], geo_type__name=v)
            except:
                geo = CensusGeography(geo_id=row[1], display_name=row[3].split(',')[0], info_text='derp')
                geo.geo_type = GeographyType.objects.get(name=v)
                geo.save()
            #TODO: add the two races data when parsing CA data
            ct_row = CensusTableRow(geography=geo, total_population=row[4], total_population_one_race=row[5],\
            total_white=row[6], total_black=row[7], total_indian=row[8], total_asian=row[9], \
            total_islander=row[10], total_other=row[11],\
            table_name='race', table_year='2000')
            ct_row.save()

    race_files = {'dataapps/census2010/data/il_sample_2000_county_hispanic.csv':'county',
    'dataapps/census2010/data/il_sample_2000_city_hispanic.csv':'place',
    'dataapps/census2010/data/il_sample_2000_legislative_upper_hispanic.csv':'legislative_upper'
    }
    for k, v in race_files.items():
        for row in reader(open(k, 'rb')):
            try:
                geo = CensusGeography.objects.get(geo_id=row[1], geo_type__name=v)
            except:
                geo = CensusGeography(geo_id=row[1], display_name=row[3].split(',')[0], info_text='derp')
                geo.geo_type = GeographyType.objects.get(name=v)
                geo.save()
            ct_row = CensusTableRow(geography=geo, total_population=row[4], total_population_one_race=row[7],\
            total_white=row[8], total_black=row[9], total_indian=row[10], total_asian=row[11], \
            total_islander=row[12], total_other=row[13], total_hispanic=row[5], total_not_hispanic=row[6],\
            table_name='hispanic', table_year='2000')
            ct_row.save()



def get_auth_ft_client():
    token = ClientLogin().authorize('baycitizendata@baycitizen.org', 'd0naten0w')
    return ftclient.ClientLoginFTClient(token)

def filter_fusion_table(geot_name):
    """
    remove the rows in a fusion table that are not in our database
    for a particular geo_type
    """
    ft_client = get_auth_ft_client()
    obj_list = list(CensusGeography.objects.filter(geo_type__name=geot_name))
    obj_names = []
    for i in obj_list:
        obj_names.append(i.geo_id)
    row_select = "SELECT ROWID, GEOID10 FROM %s" % views.FT_TABLE_IDS[geot_name]
    base_results = ft_client.query(row_select)
    base_res_list = base_results.split('\n')
    print base_res_list.pop()#pop the last empty item from the str
    result_values = []
    for idx, item in enumerate(base_res_list[1:]):
        obj = item.split(',')
        if obj[1] not in obj_names:
            result_values.append(obj)

    for idx, item in enumerate(result_values):
        del_query = "DELETE FROM %s WHERE ROWID=\'%s\'" % (views.FT_TABLE_IDS[geot_name], item[0])
        base_results = ft_client.query(del_query)
        print base_results
        print "%s,%s" % (del_query, base_results)#off by 6 places

def populate_ft_populations(geo_type_name, pop_change_field, ft_old, ft_new, ft_pct_change):

    ft_client = get_auth_ft_client()
    obj_list = list(CensusGeography.objects.filter(geo_type__name=geo_type_name))
    high_delta = 0.1
    low_delta = 0
    for obj in obj_list:
        try:
            old_ctr = CensusTableRow.objects.get(geography=obj, table_year='2000', table_name='hispanic')
            new_ctr = CensusTableRow.objects.get(geography=obj, table_year='2010', table_name='hispanic')
            delta = float(utils.get_pct_change(old_ctr, new_ctr, pop_change_field))
            if delta > high_delta:
                high_delta = delta
            if delta < low_delta:
                low_delta = delta
            row_select = "SELECT ROWID FROM %s WHERE GEOID10='%s'" % (views.FT_TABLE_IDS[geo_type_name], obj.geo_id)
            base_results = ft_client.query(row_select)
            base_res_list = base_results.split('\n')
            for idx, item in enumerate(base_res_list[1:]):
                if item != '':
                    update_str = "UPDATE %s SET %s='%s' where ROWID=\'%s\'" \
                    % (views.FT_TABLE_IDS[geo_type_name], ft_pct_change, delta, item)
                    print update_str
                    ft_client.query(update_str)
                    update_str = "UPDATE %s SET %s=%s WHERE ROWID='%s'" % (views.FT_TABLE_IDS[geo_type_name], ft_old, old_ctr.total_population, item)
                    print update_str
                    ft_client.query(update_str)
                    update_str = "UPDATE %s SET %s=%s WHERE ROWID='%s'" % (views.FT_TABLE_IDS[geo_type_name], ft_new, new_ctr.total_population, item)
                    print update_str
                    ft_client.query(update_str)
        except Exception as e:
            print "EXCEPTION=%s geoid=%s" % (e, obj.geo_id)
    print high_delta
    print low_delta


def populate_ft_slugs(geo_type_name):

    ft_client = get_auth_ft_client()
    obj_list = list(CensusGeography.objects.filter(geo_type__name=geo_type_name))
    for obj in obj_list:
        try:
            slug = obj.slug
            row_select = "SELECT ROWID FROM %s WHERE GEOID10='%s'" % (views.FT_TABLE_IDS[geo_type_name], obj.geo_id)
            base_results = ft_client.query(row_select)
            base_res_list = base_results.split('\n')
            for idx, item in enumerate(base_res_list[1:]):
                if item != '':
                    update_str = "UPDATE %s SET slug='%s' where ROWID=\'%s\'" % (views.FT_TABLE_IDS[geo_type_name], slug, item)
                    print update_str
                    ft_client.query(update_str)
        except Exception as e:
            print "EXCEPTION=%s geoid=%s" % (e, obj.geo_id)

def populate_ft_intersecting_geoid(geo_type_name, field_name, sub_geo_type):
    """
    update a fusion table's column (field_name) with the parent geography it
    intersects
    geo_type_name = the name of the geography type for the parent objects
    field_name = fusion table field to populate
    sub_geo_type = the name of the subgeographies to pull out, right now tract or place
    """
    ft_client = get_auth_ft_client()
    #get parent objs
    obj_list = CensusGeography.objects.filter(geo_type__name=geo_type_name)
    for obj in obj_list:
        obj_geo_id = obj.geo_id
        #get the subgeotype, tract or place
        sub_geos = obj.intersecting_geos.filter(geo_type__name=sub_geo_type)
        print len(sub_geos)
        try:
            for sub_geo in sub_geos:
                #get rowid from tract or place ft
                row_select = "SELECT ROWID FROM %s WHERE GEOID10='%s'" % (views.FT_TABLE_IDS[sub_geo_type], sub_geo.geo_id)
                base_results = ft_client.query(row_select)
                base_res_list = base_results.split('\n')
                for idx, item in enumerate(base_res_list[1:]):
                    if item != '':
                        update_str = "UPDATE %s SET %s='%s' where ROWID='%s'" % (views.FT_TABLE_IDS[sub_geo_type], field_name, obj_geo_id, item)
                        print update_str
                        ft_client.query(update_str)
        except Exception as e:
            print "EXCEPTION=%s geoid=%s subgeo_id=%s" % (e, obj.geo_id, sub_geo.geo_id)


def sf_blocks_p5_2010():
    filename = 'dataapps/census2010/data/DEC_10_SF1_P5_block.csv'
    rows = list(reader(open(filename, 'rb')))
    for row in rows[4:]:
        ctr = CensusTableP5Row(year=2010, geo_id='0'+row[1], total=row[3],\
         white=row[5], black=row[6], indian=row[7], asian=row[8], hawaiin=row[9],\
         other=row[10],hispanic=row[12]).save(using='boundary_db')
        print ctr

def sf_blocks_p12_2010():
    filename = 'dataapps/census2010/data/DEC_10_SF1_P12.csv'
    rows = list(reader(open(filename, 'rb')))
    for row in rows[4:]:
        ctr = CensusTableP12Row(year=2010, geo_id='0'+row[1], total=row[3], male=row[4],\
         male_under_18=int(row[5])+int(row[6])+int(row[7])+int(row[8]),\
         male_18_24=int(row[9])+int(row[10])+int(row[11])+int(row[12]),\
         male_25_29=row[13], male_30_34=row[14], male_35_39=row[15], male_40_49=int(row[16])+int(row[17]),\
         male_50_59=int(row[18])+int(row[19]),\
         male_60_84=int(row[20])+int(row[21])+int(row[22])+int(row[23])+int(row[24])+int(row[25])+int(row[26]),\
         male_85_plus=row[27],\
         female=row[28], female_under_18=int(row[29])+int(row[30])+int(row[31])+int(row[32]),\
         female_18_24=int(row[33])+int(row[34])+int(row[35])+int(row[36]),\
         female_25_29=row[37], female_30_34=row[38], female_35_39=row[39],\
         female_40_49=int(row[40])+int(row[41]), female_50_59=int(row[42])+int(row[43]),\
         female_60_84=int(row[44])+int(row[45])+int(row[46])+int(row[47])+int(row[48])+int(row[49])+int(row[50]),\
         female_85_plus=row[51])
        ctr.save(using='boundary_db')
