from bc_data_apps.apps.locations.models import Coordinates


def run():
    for c in Coordinates.objects.all():
        if c.city and c.county:
            c.city.county = c.county
            c.city.save()