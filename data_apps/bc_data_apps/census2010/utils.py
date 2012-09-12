from models import *
import inspect

def pct_change(old_val, new_val):
	try:
		return "%.1f" % ((new_val - old_val)/float(old_val)*100)
	except:
		return "--"
	
def get_pct_change(old_tablerow, new_tablerow, field_name):
	"""
	get the percentage change between two table rows
	old_tablerow: an instance of CensusTableYear with table_year='2000'
	new_tablerow: an instance of CensusTableYear with table_year='2010' 
	"""
	if old_tablerow.table_year != '2000':
		return 'incompatible comparison'
	if new_tablerow.table_year != '2010':
		return 'incompatible comparison'
	old_val = getattr(old_tablerow, field_name)
	new_val = getattr(new_tablerow, field_name)
	return pct_change(old_val, new_val)

def get_pct_change_by_field_geo_table(geo_type, table_name, field_name):
	"""
	loop through all rows of both 2010 and 2000 tables for a particular geotype and table
	return a tuple containg the old total value, the new total value and pct change
	"""
	geographies = CensusGeography.objects.filter(geo_type=geo_type)
	total_old = 0
	total_new = 0
	for g in geographies:
		old_ctr = CensusTableRow.objects.get(geography=g, table_name=table_name, table_year='2000')
		new_ctr = CensusTableRow.objects.get(geography=g, table_name=table_name, table_year='2010')
		total_old = total_old + getattr(old_ctr, field_name)
		total_new = total_new + getattr(new_ctr, field_name)
	t_pct_change = pct_change(total_old, total_new)
	return (total_old, total_new, t_pct_change)

def do_2010_2000_pct_change():
	cgs = CensusGeography.objects.all()
	for cg in cgs:
		print cg.display_name
		old_ctr = CensusTableRow.objects.get(geography=cg, table_name='race', table_year='2000')
		new_ctr = CensusTableRow.objects.get(geography=cg, table_name='race', table_year='2010')
		print old_ctr
		print new_ctr
		print get_pct_change(old_ctr, new_ctr, 'total_population')