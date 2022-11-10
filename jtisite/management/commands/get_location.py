import pandas as pd
from django.core.management import BaseCommand

from jtisite.management.commands.location_api import get_country_and_city


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('lat', type=float)
        parser.add_argument('lon', type=float)

    def handle(self, *args, **options):
        coordinates = (options['lat'], options['lon'])
        df = pd.read_excel('sites.xlsx').fillna('')
        for item, value in df.iterrows():
            if value['Coordinates']:
                coordinates = value['Coordinates'][1:-1].split(', ')
                city_name, country_name = get_country_and_city(coordinates)
                country_name = get_country_and_city(coordinates)
                print(city_name, country_name)
                print(item, country_name)
