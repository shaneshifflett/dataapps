school_county_cities_query = """
SELECT
  DISTINCT c.id id,
  c.name
FROM
  locations_city c
  JOIN schools_school s ON c.id = s.city_id
WHERE
  c.county_id = %s
ORDER BY c.name
"""