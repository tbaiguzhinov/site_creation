import os

import pandas as pd
import requests
from django.core.management import BaseCommand
from dotenv import load_dotenv

from jtisite.management.commands.resolver_api import authenticate
from jtisite.models import Country, Region


def get_all_objects(token, objectTypeId):
    all_objects = []
    page = 1
    objects = [1]
    while objects:
        print('Getting page', page)
        objects_url = "https://eu.core.resolver.com/data/object?objectTypeId={}&pageNumber={}".format(
            objectTypeId, page)
        header = {"Authorization": f"bearer {token}"}
        objects = requests.get(objects_url, headers=header).json()['data']
        for object_ in objects:
            all_objects.append(object_)
        page += 1
    return all_objects


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('objectTypeId', type=int)

    def handle(self, *args, **options):
        load_dotenv()
        token = authenticate(
            login=os.getenv('EMAIL'),
            password=os.getenv('PASSWORD'),
        )
        objectTypeId = options['objectTypeId']
        objects = get_all_objects(token, objectTypeId)
        df = pd.read_excel(
            r'C:\Users\MOSBAIGUT\Downloads\reportExport_countries_and_cities__11092022_724PM.xlsx',
            sheet_name='Table-3',
        ).fillna('')
        for item, data in df.iterrows():
            country = Country.objects.get(name=data['Country Name'])
            region = Region.objects.get(name=data['JTI Region Name'])
            country.region = region
            country.save()
