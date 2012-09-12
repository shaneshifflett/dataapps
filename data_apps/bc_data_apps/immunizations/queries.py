high_iz_schools_query = """
    SELECT
      s.id id,
      (100 * (SUM(i.up_to_date_number) / SUM(i.enrollment))) iz_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_county c ON s.county_id = c.id
    WHERE
      c.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      s.id
    ORDER BY 
      iz_percent desc, c.name
    LIMIT 3
"""

low_iz_schools_query = """
    SELECT
      s.id id,
      (100 * (SUM(i.up_to_date_number) / SUM(i.enrollment))) iz_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_county c ON s.county_id = c.id
    WHERE
      c.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      s.id
    ORDER BY 
      iz_percent asc, c.name
    LIMIT 3
"""

high_pbe_schools_query = """
    SELECT
      s.id id,
      (100 * (SUM(i.pbe_number) / SUM(i.enrollment))) pbe_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_county c ON s.county_id = c.id
    WHERE
      c.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      s.id
    ORDER BY 
      pbe_percent desc, c.name
    LIMIT 3
"""

low_pbe_schools_query = """
    SELECT
      s.id id,
      (100 * (SUM(i.pbe_number) / SUM(i.enrollment))) pbe_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_county c ON s.county_id = c.id
    WHERE
      c.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      s.id
    ORDER BY 
      pbe_percent asc, c.name
    LIMIT 3
"""

high_iz_districts_query = """
    SELECT
      d.id id,
      (100 * (SUM(i.up_to_date_number) / SUM(i.enrollment))) iz_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN schools_schooldistrict d ON s.district_id = d.id
      JOIN locations_county co ON s.county_id = co.id
    WHERE
      co.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      d.id
    ORDER BY 
      iz_percent desc, d.name
    LIMIT 3
"""

low_iz_districts_query = """
    SELECT
      d.id id,
      (100 * (SUM(i.up_to_date_number) / SUM(i.enrollment))) iz_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN schools_schooldistrict d ON s.district_id = d.id
      JOIN locations_county co ON  s.county_id = co.id
    WHERE
      co.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      d.id
    ORDER BY 
      iz_percent asc, d.name
    LIMIT 3
"""

high_pbe_districts_query = """
    SELECT
      d.id id,
      (100 * (SUM(i.pbe_number) / SUM(i.enrollment))) pbe_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN schools_schooldistrict d ON s.district_id = d.id
      JOIN locations_county co ON s.county_id = co.id
    WHERE
      co.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      d.id
    ORDER BY 
      pbe_percent desc, d.name
    LIMIT 3
"""

low_pbe_districts_query = """
    SELECT
      d.id id,
      (100 * (SUM(i.pbe_number) / SUM(i.enrollment))) pbe_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN schools_schooldistrict d ON s.district_id = d.id
      JOIN locations_county co ON s.county_id = co.id
    WHERE
      co.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      d.id
    ORDER BY 
      pbe_percent asc, d.name
    LIMIT 3
"""

high_iz_cities_query = """
    SELECT
      c.id id,
      (100 * (SUM(i.up_to_date_number) / SUM(i.enrollment))) iz_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_city c ON s.city_id = c.id
      JOIN locations_county co ON c.county_id = co.id
    WHERE
      co.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      c.id
    ORDER BY 
      iz_percent desc, c.name
    LIMIT 3
"""

low_iz_cities_query = """
    SELECT
      c.id id,
      (100 * (SUM(i.up_to_date_number) / SUM(i.enrollment))) iz_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_city c ON s.city_id = c.id
      JOIN locations_county co ON  c.county_id = co.id
    WHERE
      co.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      c.id
    ORDER BY 
      iz_percent asc, c.name
    LIMIT 3
"""

high_pbe_cities_query = """
    SELECT
      c.id id,
      (100 * (SUM(i.pbe_number) / SUM(i.enrollment))) pbe_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_city c ON s.city_id = c.id
      JOIN locations_county co ON c.county_id = co.id
    WHERE
      co.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      c.id
    ORDER BY 
      pbe_percent desc, c.name
    LIMIT 3
"""

low_pbe_cities_query = """
    SELECT
      c.id id,
      (100 * (SUM(i.pbe_number) / SUM(i.enrollment))) pbe_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_city c ON s.city_id = c.id
      JOIN locations_county co ON c.county_id = co.id
    WHERE
      co.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      c.id
    ORDER BY 
      pbe_percent asc, c.name
    LIMIT 3
"""

high_iz_counties_query = """
    SELECT
      c.id id,
      (100 * (SUM(i.up_to_date_number) / SUM(i.enrollment))) iz_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_county c ON s.county_id = c.id
    WHERE
      c.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      c.id
    ORDER BY 
      iz_percent desc, c.name
    LIMIT 3
"""

low_iz_counties_query = """
    SELECT
      c.id id,
      (100 * (SUM(i.up_to_date_number) / SUM(i.enrollment))) iz_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_county c ON s.county_id = c.id
    WHERE
      c.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      c.id
    ORDER BY 
      iz_percent asc, c.name
    LIMIT 3
"""

high_pbe_counties_query = """
    SELECT
      c.id id,
      (100 * (SUM(i.pbe_number) / SUM(i.enrollment))) pbe_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_county c ON s.county_id = c.id
    WHERE
      c.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      c.id
    ORDER BY 
      pbe_percent desc, c.name
    LIMIT 3
"""

low_pbe_counties_query = """
    SELECT
      c.id id,
      (100 * (SUM(i.pbe_number) / SUM(i.enrollment))) pbe_percent
    FROM
      immunizations_schoolimmunization i
      JOIN schools_school s ON i.school_id = s.id
      JOIN locations_county c ON s.county_id = c.id
    WHERE
      c.slug IN('alameda', 'contra-costa', 'marin', 'napa', 'san-francisco', 'san-mateo', 'santa-clara', 'solano', 'sonoma' )
      AND
      i.year=2010
    GROUP BY
      c.id
    ORDER BY 
      pbe_percent asc, c.name
    LIMIT 3
"""
