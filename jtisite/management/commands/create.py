import os

from django.core.management import BaseCommand
from dotenv import load_dotenv

from jtisite.management.commands.resolver_api import (authenticate,
                                                      create_new_site,
                                                      search_objects,
                                                      update_object,
                                                      create_assessment,
                                                      trigger_workflow,
                                                      get_related_objects,
                                                      relate_objects,
                                                      get_country_risks
                                                      )

request_type_id = 8063
request_active = 31056
request_type_field = 42977
site_create_request = 122005


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_dotenv()
        token = authenticate(
            login=os.getenv('EMAIL'),
            password=os.getenv('PASSWORD'),
        )
        # new_requests = []
        # open_requests = search_objects(
        #     token=token,
        #     objectTypeId=request_type_id,
        #     lifeCycleId=request_active,
        # )
        # for request in open_requests:
        #     request_type = request['evaluations'][
        #         str(request_type_field)
        #         ]['value'] if str(
        #         request_type_field) in request['evaluations'] else None
        #     if request['objectLifeCycleStateId'] == request_active \
        #             and request_type == site_create_request:
        #         new_requests.append(request)

        new_requests = [{'id': 1439566, 'name': 'Medium priority request #2022-620: JTI Site: add new  ', 'description': 'Warehouse for the storage of all POSM material', 'externalRefId': 'f54b5030-1c5d-4a36-a896-fee6f95c7b33', 'uniqueId': '620', 'objectTypeId': 8063, 'evaluations': {'37037': {'value': None}, '37042': {'value': None}, '37048': {'value': None}, '37052': {'value': 97861}, '37055': {'value': 0}, '37064': {'value': None}, '37083': {'value': 98204}, '37085': {'value': None}, '37090': {'value': 0}, '37091': {'value': [{'id': 27102, 'displayFileName': 'PHOTO-2022-10-13-13-27-57 (3).jpg'}, {'id': 27103, 'displayFileName': 'PHOTO-2022-10-13-13-27-58 (1).jpg'}, {'id': 27104, 'displayFileName': 'PHOTO-2022-10-13-13-27-58 (2).jpg'}, {'id': 27105, 'displayFileName': 'PHOTO-2022-10-13-13-27-58.jpg'}]}, '37093': {'value': 97832}, '37095': {'value': None}, '37098': {'value': 97796}, '37103': {'value': 0}, '37125': {'value': None}, '37128': {'value': None}, '40607': {'value': 0}, '40608': {'value': 0}, '40609': {'value': None}, '40610': {'value': None}, '40611': {'value': None}, '40612': {'value': 86}, '40613': {'value': 115000}, '40615': {'value': 115447}, '42977': {'value': 122005}, '51531': {'value': None}, '51551': {'value': 1357084800}, '51565': {'value': {'x': 0, 'y': 0, 'name': 'PHOTO-2022-10-13-13-27-57.jpg', 'width': 0, 'height': 0, 'cropped': 0, 'original': 27100, 'compressed': 27101, 'description': ''}}, '51620': {'value': 'No. 1 Awosika Avenue, Ikeja Industrial Estate, Ikeja, Lagos.'}, '52410': {'value': None}, '54124': {'value': None}, '61157': {'value': None}}, 'formulas': {}, 'objectLifeCycleStateId': 31056, 'created': '2022-11-02T07:44:51.718Z', 'createdBy': 2965, 'modified': '2022-11-11T07:17:05.104Z', 'modifiedBy': 2922, 'dateStateChanged': '2022-11-11T07:17:05.163Z', 'assessment': False, 'anchor': None, 'dimensions': [], 'uniqueIdArray': [620], 'assessmentObjectId': None, 'assessmentObjectTypeId': None, 'assessmentLaunched': None, 'last_trigger_time': '2022-11-11T07:17:05.150Z', 'is_archive': False, 'geolocation': {'id': 42655, 'geo': {'type': 'Point', 'coordinates': [6.61166191, 3.339634539]}, 'country': 'NGA', 'countryName': 'Nigeria', 'state': '', 'stateName': 'Lagos', 'city': 'Lagos', 'zipCode': '', 'street': 'Awosika Ave', 'houseNumber': '', 'notes': '', 'created': '2022-11-02T07:44:50.874Z', 'label': 'Awosika Ave, Ikeja, Nigeria'}, 'geolocation_id': 42655, 'lastSyncDate': None, 'submitter': None, 'submitterName': None, 'submitterType': None, 'creationType': None, 'isSubmitterAnonymous': False, 'hasSubmitterOptedIn': False, 'creationEmailAddressId': None, 'canWrite': False, 'elasticScore': 3}]
        print('Processing {} new requests'.format(len(new_requests)))
        for request in new_requests:
            request_order = request['id']
            print(f'working on requset No {request_order}')
            print('...creating site')
            site_id, site_name, description, country_id, region_id, trigger_id_for_csa = create_new_site(
                token, request)
            update_object(token, objectId=site_id,
                          name=site_name, description=description)
            print(f'{site_name} created')
            print('...creating assessment')
            assessment_id = create_assessment(token, site_name, site_id)
            relate_objects(
                token=token,
                objectId=assessment_id,
                relatedObjectId=304124,
                relationshipTypeId=18885,
                params={'shouldClone': 'true'}
            )
            relate_objects(
                token=token,
                objectId=assessment_id,
                relatedObjectId=304125,
                relationshipTypeId=18885,
                params={'shouldClone': 'true'}
            )
            print('...confirming scope')
            trigger_workflow(token, objectId=assessment_id, triggerId=38600)
            print('...renaming presets')
            presets = get_related_objects(
                token=token,
                objectId=assessment_id,
                relationshipTypeId=18885,
            )
            for preset in presets:
                if 'Corporate Security Audit' in preset['externalRefId']:
                    csa_preset_id = preset['objectId']
                elif 'Security Risk Assessment' in preset['externalRefId']:
                    srm_preset_id = preset['objectId']
            update_object(token, objectId=csa_preset_id,
                          name=f'CSA: {site_name}')
            update_object(token, objectId=srm_preset_id,
                          name=f'SRM: {site_name}')
            print('...linking presets to region')
            relate_objects(
                token=token,
                objectId=region_id,
                relatedObjectId=csa_preset_id,
                relationshipTypeId=25333,
            )
            relate_objects(
                token=token,
                objectId=region_id,
                relatedObjectId=srm_preset_id,
                relationshipTypeId=25333,
            )
            print('...getting risks linked to SRM preset')
            risks = get_related_objects(
                token=token,
                objectId=srm_preset_id,
                relationshipTypeId=18899
            )
            print('...getting risks linked to country')
            country_risks = get_country_risks(token, country_id)
            print('...linking SRM risks to Country risks')
            for risk in risks:
                update_object(
                    token, objectId=risk['objectId'], description=site_name)
                relate_objects(
                    token,
                    objectId=risk['objectId'],
                    relatedObjectId=country_risks[risk['objectName']],
                    relationshipTypeId=18879
                )
            print('...triggering CSA applicability')
            trigger_workflow(token, objectId=csa_preset_id,
                             triggerId=trigger_id_for_csa)
            print('...archiving request')
            trigger_workflow(token, objectId=request['id'], triggerId=22578)
            print('End of script')
