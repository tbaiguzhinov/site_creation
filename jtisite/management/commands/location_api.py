import os

from dotenv import load_dotenv
from googlemaps import Client


def get_country_and_city(lat, lon):
    load_dotenv
    gmaps = Client(key=os.getenv('GOOGLE_API'))
    reverse_geocode_result = gmaps.reverse_geocode(
        (lat, lon),
        language='en',
        result_type=['locality'],
    )
    locations = reverse_geocode_result[0]['address_components']
    city_name = None
    country_name = None
    for elem in locations:
        if 'country' in elem['types']:
            country_name = elem['long_name']
        elif 'locality' in elem['types']:
            city_name = elem['long_name']
    return city_name, country_name