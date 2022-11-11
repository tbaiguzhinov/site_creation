import time

import requests

from jtisite.management.commands.location_api import get_country_and_city


class MissingFieldError(Exception):
    pass


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
    site_fields = {
        '37052': 'Site category',
        '37055': 'jti_staff',
        '37083': 'Operated by',
        '37085': 'fg',
        '37090': 'ia_sta',
        '37093': 'Site type',
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
        '51620': 'legal address',
    }
    required_fields = ['37052', '37083', '37093', '51620']
    staff_fields = ['37055', '37090', '37103', '40607', '40608']
    finance_fields = ['37085', '40609', '40610', '40611', '40612', '40613']
    evaluations = []
    for fieldId, value_field in request['evaluations'].items():
        value = value_field['value']
        if fieldId == '51551' and not value:
            value = time.time()
        if fieldId in site_fields and value:
            evaluations.append({
                'fieldId': fieldId,
                'value': value,
            })
        if (fieldId in staff_fields or fieldId in finance_fields) and not value:
            evaluations.append({
                'fieldId': fieldId,
                'value': '0',
            })
        if fieldId in required_fields and not value:
            field_name = site_fields[fieldId]
            raise MissingFieldError(f'{field_name} is missing')
    files = get_file(token, request_id=request['id'])
    photo = files['51565'][0] if '51565' in files else None
    cs_responsibles = None
    roles = get_cs_responsible(token, request_id=request['id'])[
        'roleEvaluations']
    for role in roles:
        if role['roleId'] == '4359' and role['users']:
            cs_responsibles = role['users']
    geolocation = request['geolocation']
    geolocation.pop('id')
    geolocation.pop('created')

    city_obj, site_type, site_category, icon = get_site_type_category_city(
        site_type_id=request['evaluations']['37093']['value'],
        site_category_id=request['evaluations']['37052']['value'],
        geolocation=geolocation,
    )
    trigger_id_for_csa = get_trigeer_id_for_csa(site_category, site_type)
    name = create_site_name(
        icon,
        city_obj.name,
        city_obj.country.name,
        site_type,
        site_category,
        comments=None,
    )
    blank_ref_id = create_ref_id(city_obj.name, site_type, site_category)
    externalRefId = check_for_ref_id(
        token, blank_ref_id, city_obj.country.simp_id)
    description = get_description(
        operated_by=request['evaluations']['37083']['value'],
        site_type=site_type,
        site_category=site_category,
        address=request['evaluations']['51620']['value'],
        coordinates=geolocation['geo']['coordinates'],
    )
    country_id = city_obj.country.simp_id
    region_id = city_obj.country.region.simp_id
    data = {
        'name': name,
        'externalRefId': externalRefId,
        'description': description,
        'evaluations': evaluations,
        'geolocation': geolocation,
        'objectTypeId': 8100,
        'references': [
            {
                'relationshipId': '13345',
                'value': [country_id]
            },
            {
                'relationshipId': '14575',
                'value': [region_id]
            },
            {
                'relationshipId': '28461', # Linking to AdminConnect
                'value': [1384357]
            },
        ],
        'triggerId': '22562',
    }
    if photo:
        data['files'] = [
            {
                'fileId': photo['id'],
                'fieldId': 51565,
            }
        ]
    if cs_responsibles:
        data['roles'] = [{
            'roleId': '4359',
            'users': cs_responsibles,
        }]
    response = requests.post(
        'https://eu.core.resolver.com/creation/creation',
        headers={'Authorization': f'Bearer {token}'},
        json=data,
    )
    response.raise_for_status()
    return response.json()['id'], name, description, country_id, region_id, trigger_id_for_csa


def get_trigeer_id_for_csa(site_category, site_type):
    triggers = {
        "WH B": 44622,
        "WH A": 44620,
        "Office C": 44618,
        "Office B": 44616,
        "Office A": 44614,
        "Leaf WH": 44612,
        "Leaf Factory": 44610,
        "FG Factory": 44608,
        "CDWH": 44606,
        "WH C": 43463,
    }
    if site_type == 'Sales Depot':
        return triggers['WH C']
    elif site_type == 'Factory':
        return triggers['FG Factory']
    elif site_type == 'Cross-Docking WH':
        return triggers['CDWH']
    elif site_type == 'Leaf WH':
        return triggers['Leaf WH']
    elif site_type == 'Leaf Factory':
        return triggers['Leaf Factory']
    if site_category == 'A':
        if site_type == 'FG WH':
            return triggers['WH A']
        elif site_type == 'Office':
            return triggers['Office A']
    elif site_category == 'B':
        if site_type == 'Office':
            return triggers['Office B']
        else:
            return triggers['WH B']
    else:
        if site_type == 'C':
            return triggers['Office C']
        return triggers['WH C']


def get_site_type_category_city(site_type_id, site_category_id, geolocation):
    icons_and_types = {
        97700: (chr(127981), 'Factory'),
        98188: (chr(127981)+chr(127810), 'Leaf Factory'),
        98770: (chr(127968), 'Office'),
        98279: (chr(128230)+chr(128684), 'FG WH'),
        97761: (chr(128230)+chr(127810), 'Leaf WH'),
        115449: (chr(128230), 'Sales Depot'),
        98779: (chr(128230), 'Cross-Docking WH'),
        97832: (chr(128230), 'M&S WH'),
        98537: (chr(128230), 'NTM WH'),
    }
    categories = {
        98482: 'A',
        98436: 'B',
        97861: 'C',
    }
    icon, site_type = icons_and_types[site_type_id]
    city_obj = get_country_and_city(geolocation)
    site_category = categories[site_category_id]
    return city_obj, site_type, site_category, icon


def create_site_name(icon, city, country, site_type, site_category, comments):
    name = f'{icon}{city}, {country}: {site_type} cat. {site_category}'
    if comments:
        name += f' ({comments})'
    return name


def create_ref_id(city, site_type, site_category):
    return f'{city} ({site_type} {site_category})'


def get_sites_from_country(token, objectId, relationshipTypeId=13345):
    response = requests.get(
        f'https://eu.core.resolver.com/data/object/{objectId}/relationships/{relationshipTypeId}',
        headers={'Authorization': f'Bearer {token}'},
    )
    response.raise_for_status()
    return response.json()


def check_for_ref_id(token, blank_ref_id, country_simp_id):
    all_sites = get_sites_from_country(token, country_simp_id)
    all_externalrefids = [site['externalRefId'] for site in all_sites]
    x = 1
    suggested_refId = '{} {:02d}'.format(blank_ref_id, x)
    while suggested_refId in all_externalrefids:
        x += 1
        suggested_refId = '{} {:02d}'.format(blank_ref_id, x)
    return suggested_refId


def get_description(
    operated_by,
    site_type,
    site_category,
    address,
    coordinates
):
    operated_options = {
        98799: 'JTI',
        98204: '3PL',
        186736: 'Other (Specify)',
    }
    operated_by = operated_options[operated_by]
    lat, lon = coordinates
    return f'{operated_by} operated {site_type} {site_category} at: {address} (GPS: {lat}, {lon})'


def get_cs_responsible(token, request_id):
    response = requests.get(
        f'https://eu.core.resolver.com/data/object/{request_id}/roleMembership',
        headers={'Authorization': f'Bearer {token}'},
    )
    response.raise_for_status()
    return response.json()


def get_file(token, request_id):
    response = requests.get(
        f'https://eu.core.resolver.com/data/object/{request_id}/file',
        headers={'Authorization': f'Bearer {token}'},
    )
    response.raise_for_status()
    return response.json()


def create_assessment(token, name, jti_site_id):
    data = {
        'name': name,
        'objectTypeId': 11307,
        'relationships': [
            {
                'relationshipId': 18898,
                'value': [jti_site_id]
            },
            {
                'relationshipId': 18892,
                'value': [304126]
            }
        ],
        'evaluations': [
            {
                'fieldId': 51533,  # Assessment Type
                'value': 149233  # Site
            }
        ],
        'assessment': 'true',
        'dimensions': [
            {
                'type': 1,
                'optionId': jti_site_id,
                'dimensionId': 8100,  # Site
            }
        ],
        'triggerId': 38480,
        'parent': {
            'inverse': 'true',
            'objectId': jti_site_id,
            'relationshipTypeId': 18898
        }
    }
    response = requests.post(
        'https://eu.core.resolver.com/creation/creation',
        headers={'Authorization': f'Bearer {token}'},
        json=data,
    )
    response.raise_for_status()
    return response.json()['id']


def add_assesment_focus(token, assessment_id, objectId):
    data = {
        'objectId': objectId,
    }
    response = requests.post(
        f'https://eu.core.resolver.com/creation/assessment/{assessment_id}/focus',
        headers={'Authorization': f'Bearer {token}'},
        json=data,
    )
    response.raise_for_status()
    return response.json()


def launch_assessment(token, assessment_id):
    response = requests.post(
        f'https://eu.core.resolver.com/creation/assessment/{assessment_id}/launch',
        params={'useJob': 'true'},
        headers={'Authorization': f'Bearer {token}'},
    )
    response.raise_for_status()
    return response.json()['id']


def poll_for_status(token, jobId):
    status = 1
    while status == 1:
        response = requests.get(
            f'https://eu.core.resolver.com/object/job/{jobId}',
            headers={
                'Authorization': f'Bearer {token}',
            },
        )
        response.raise_for_status()
        status = response.json()['status']
        time.sleep(15)
    return 'Success'


def trigger_workflow(token, objectId, triggerId):
    response = requests.post(
        f'https://eu.core.resolver.com/data/object/{objectId}/trigger/{triggerId}/go',
        headers={'Authorization': f'Bearer {token}'},
        params={'tz': 'Asia/Almaty'},
    )
    response.raise_for_status()
    return response.json()


def get_related_objects(token, objectId, relationshipTypeId):
    response = requests.get(
        f'https://eu.core.resolver.com/data/object/{objectId}/relationships/{relationshipTypeId}',
        headers={'Authorization': f'Bearer {token}'},
    )
    response.raise_for_status()
    return response.json()


def update_object(token, objectId, name=None, description=None):
    data = {}
    if name:
        data['name'] = name
    if description:
        data['description'] = description
    response = requests.put(
        f'https://eu.core.resolver.com/data/object/{objectId}',
        headers={'Authorization': f'Bearer {token}'},
        json=data,
    )
    response.raise_for_status()


def relate_objects(
    token,
    objectId,
    relatedObjectId,
    relationshipTypeId=18879,
    params=None
):
    response = requests.post(
        f'https://eu.core.resolver.com/creation/creation/{objectId}/relationship/{relationshipTypeId}/relatedObject/{relatedObjectId}',
        headers={'Authorization': f'Bearer {token}'},
        params=params,
    )
    status_code = response.status_code
    if status_code >= 300:
        print(f'...loaded with status code {status_code}, sleeping 15 seconds')
        time.sleep(15)


def get_country_risks(token, country_id):
    risks = {}
    country_assessment_id = get_related_objects(
        token=token,
        objectId=country_id,
        relationshipTypeId=18883,
    )[0]['objectId']
    country_presets = get_related_objects(
        token=token,
        objectId=country_assessment_id,
        relationshipTypeId=18885,
    )
    srm_preset_id = 0
    for preset in country_presets:
        if 'SRM' in preset['objectName']:
            srm_preset_id = preset['objectId']
    if not srm_preset_id:
        raise
    country_risks = get_related_objects(
        token=token,
        objectId=srm_preset_id,
        relationshipTypeId=18899
    )
    for risk in country_risks:
        risks[risk['objectName']] = risk['objectId']
    return risks


def change_field(token, value, objectId, fieldId):
    data = {
        'value': value,
    }
    response = requests.post(
        f'https://eu.core.resolver.com/data/object/{objectId}/evaluation/field/{fieldId}',
        headers={'Authorization': f'Bearer {token}'},
        json=data,
    )
    response.raise_for_status()
    return response.json()