import os

from dotenv import load_dotenv
from googlemaps import Client

from jtisite.models import City, Country, Location

country_converter = {
    'Myanmar (Burma)': 'Myanmar',
    'United States': 'USA',
    'Czechia': 'Czech Republic',
    'United Kingdom': 'UK',
    'United Arab Emirates': 'UAE',
    'Democratic Republic of the Congo': 'DR Congo',
}


def get_country_and_city(geolocation):
    lat, lon = geolocation['geo']['coordinates']
    try:
        location = Location.objects.get(
            lat=lat,
            lon=lon,
        )
        return location.city
    except Location.DoesNotExist:
        pass
    city_name = geolocation['city'] if 'city' in geolocation else None
    country_name = geolocation['country_name'] if 'country_name' in geolocation else None
    if not city_name or not country_name:
        return google_maps_geocoding(lat, lon)
    if country_name in country_converter:
        country_name = country_converter[country_name]
    try:
        country = Country.objects.get(
            name=country_name,
        )
    except Country.DoesNotExist:
        print(country_name)
        raise
    
    city, created = City.objects.get_or_create(
        name=city_name,
        country=country,
    )
    Location.objects.create(
        lat=lat,
        lon=lon,
        city=city,
        country=country,
    )
    return city


def google_maps_geocoding(lat, lon):
    load_dotenv()
    gmaps = Client(key=os.getenv('GOOGLE_API'))
    reverse_geocode_result = gmaps.reverse_geocode(
        (lat, lon),
        language='en',
    )
    city_name = None
    country_name = None
    for location in reverse_geocode_result:
        for elem in location['address_components']:
            if 'country' in elem['types'] and not country_name:
                country_name = elem['long_name']
            if 'locality' in elem['types'] and not city_name:
                city_name = elem['long_name']
    if not city_name and not country_name:
        return
    if country_name in country_converter:
        country_name = country_converter[country_name]
    try:
        country = Country.objects.get(
            name=country_name,
        )
    except Country.DoesNotExist:
        print(country_name)
        raise
    
    city, created = City.objects.get_or_create(
        name=city_name,
        country=country,
    )
    Location.objects.create(
        lat=lat,
        lon=lon,
        city=city,
        country=country,
    )
    return city