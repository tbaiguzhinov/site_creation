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
        new_requests = []
        open_requests = search_objects(
            token=token,
            objectTypeId=request_type_id,
            lifeCycleId=request_active,
        )
        for request in open_requests:
            request_type = request['evaluations'][
                str(request_type_field)
                ]['value'] if str(
                request_type_field) in request['evaluations'] else None
            if request['objectLifeCycleStateId'] == request_active \
                    and request_type == site_create_request:
                new_requests.append(request)

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
