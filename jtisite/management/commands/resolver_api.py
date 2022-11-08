import requests
from xlsxwriter import Workbook


def authenticate(login, password):
    data = {
        'email': login,
        'password': password,
        'selectedOrg': 166,
        'client': 'core-client',
    }
    response = requests.post(
        'https://eu.core.resolver.com/user/authenticate',
        json=data,
    )
    response.raise_for_status()
    return response.json()['token']


def get_objects(token, objectTypeId, page):
    params = {
        'objectTypeId': objectTypeId,
        'pageNumber': page,
    }
    response = requests.get(
        'https://eu.core.resolver.com/data/object',
        headers={'Authorization': f'Bearer {token}'},
        params=params
    )
    return response.json()['data']


def search_objects(token, objectTypeId, lifeCycleId=None):
    params = {
        'objectTypeId': objectTypeId,
        'limit': 100,
    }
    if lifeCycleId:
        params['filters'] = str(
            {'objectLifeCycleStateId': str([lifeCycleId])}).replace('\'', '\"')
    response = requests.get(
        'https://eu.core.resolver.com/data/search/query',
        headers={'Authorization': f'Bearer {token}'},
        params=params,
    )
    response.raise_for_status()
    return response.json()['data'][str(objectTypeId)]['records']


def create_new_site(token, request):
    required_fields = {
        '37052': 'category',
        '37055': 'jti_staff',
        '37083': 'operated_by',
        '37085': 'fg',
        '37090': 'ia_sta',
        '37091': 'attachments',
        '37093': 'type',
        '37095': 'photo',
        '37103': 'contractors',
        '40607': 'field_force',
        '40608': 'key_staff',
        '40609': 'leaf',
        '40610': 'stamps',
        '40611': 'equipment',
        '40612': 'building',
        '40613': 'other',
        '40615': 'key_site',
        '51551': 'start_date',
        '51565': 'image2',
        '51620': 'legal_address',
    }
    evaluations = []
    for evaluation, value in request['evaluations'].items():
        if evaluation in required_fields:
            evaluations.append({
                'fieldId': evaluation,
                'value': value['value'],
            })
    name = create_site_name(
        site_type=request['evaluations']['37093']['value'],
        site_category=request['evaluations']['37052']['value'],
        location='',
    )
    print(name)
    raise
    # Identify external ref id
    # Add logo to Name concat
    # Add comments (if Available) to Name concat
    # When adding geolocation, add description from Legal address

    data = {
        "name": name,
        "externalRefId": "{ICON}{City}({SiteType} {SiteCategory}) 01 > 02 > 03",
        "description": "{Operated by} operated {SiteType} {SiteCategory} at: {Street&House}, {Postal/ZIP Code}, {City}, {Country} (GPS: {GPS coordinates})",
        "evaluations": evaluations,
        "geolocation": {
            "geo": {
                "type": "point",
                "coordinates": [
                    0,
                    0
                ]
            },
            "country": "US",
            "countryName": "United States",
            "state": "string",
            "stateName": "string",
            "city": "string",
            "zipCode": "string",
            "street": "string",
            "houseNumber": "string",
            "notes": "string",
            "label": "string"
        },
        "geolocationTranslations": [
            {
                "language": "string",
                "country": "string",
                "state": "string",
                "city": "string",
                "zipCode": "string",
                "street": "string",
                "houseNumber": "string",
                "label": "string"
            }
        ],
        "objectTypeId": "string",
        "anchor": "string",
        "relationships": [
            {
                "relationshipId": "string",
                "value": [
                    "string"
                ]
            }
        ],
        "references": [
            {
                "relationshipId": "string",
                "value": [
                    "string"
                ]
            }
        ],
        "roles": [
            {
                "roleId": "string",
                "users": [
                    "string"
                ],
                "userGroups": [
                    "string"
                ]
            }
        ],
        "files": [
            {
                "fileId": 0,
                "fieldId": 0
            }
        ],
        "triggerId": "string",
        "assessment": false,
        "dimensions": [
            {
                "type": 1,
                "dimensionId": 0,
                "optionId": 0
            }
        ],
        "hasSubmitterOptedIn": false,
        "isSubmitterAnonymous": true,
        "submitter": "string",
        "submitterName": "string",
        "parent": {
            "objectId": 0,
            "relationshipTypeId": 0,
            "inverse": false
        },
        "tz": "UTC"
    }

    response = requests.post(
        'https://eu.core.resolver.com/creation/creation',
        headers={'Authorization': f'Bearer {token}'},
        json=data,
    )
    response.raise_for_status()
    return response.json('id')


def create_site_name(site_type, site_category, location):
    icon = ''
    city = ''
    country = ''
    site_type = ''
    site_category = ''
    return f'{icon}{city}, {country}: {site_type} {site_category}'


def get_all_sites(token):
    objectTypeId = 8100
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

    wb = Workbook('sites.xlsx')
    sheet1 = wb.add_worksheet('Sheet1')
    sheet1.write(0, 1, 'Site name')
    sheet1.write(0, 2, 'Site description')
    sheet1.write(0, 3, 'Legal address')
    sheet1.write(0, 4, 'Coordinates')
    sheet1.write(0, 5, 'Address label')

    row = 1
    for object in all_objects:
        sheet1.write(row, 1, object['name'])
        sheet1.write(row, 2, object['description'])
        sheet1.write(row, 3, object['evaluations']['51620']
                     ['value'] if '51620' in object['evaluations'] else '')
        sheet1.write(row, 4, str(
            object['geolocation']['geo']['coordinates']) if 'geolocation' in object else '')
        sheet1.write(row, 5, object['geolocation']
                     ['label'] if 'geolocation' in object else '')
        row += 1
    wb.close()
