import os

from django.core.management import BaseCommand
from dotenv import load_dotenv

from jtisite.management.commands.resolver_api import (authenticate,
                                                      search_objects,
                                                      get_related_objects,
                                                      get_object,
                                                      trigger_workflow,
                                                      create_import_file,
                                                      create_site_import_file,
                                                      change_field,
                                                      )
from jtisite.management.commands.upload_file import upload_file


request_type_id = 8063
request_active = 31056
request_type_field = 42977
site_close_request = 122006


class Preset_Incomplete(Exception):
    pass


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
                    and request_type == site_close_request:
                new_requests.append(request)

        print('Processing {} new requests'.format(len(new_requests)))
        for request in new_requests:
            request_id = request['id']
            print(f'...working on request No {request_id}')
            print('...getting linked sites')
            sites = get_related_objects(
                token=token,
                objectId=request_id,
                relationshipTypeId=15572,
            )
            
            csa_is_incomplete = False
            print('...found {} site(s):'.format(len(sites)))
            for site in sites:
                print('......working with', site['objectName'])
                assessment = get_related_objects(
                    token=token,
                    objectId=site['objectId'],
                    relationshipTypeId=18898,
                )[0]
                presets = get_related_objects(
                    token=token,
                    objectId=assessment['objectId'],
                    relationshipTypeId=18885,
                )
                for preset in presets:
                    if 'Corporate Security Audit' in preset['externalRefId']:
                        csa_preset_id = preset['objectId']
                    elif 'Security Risk Assessment' in preset['externalRefId']:
                        srm_preset_id = preset['objectId']
                        srm_external_refid = preset['externalRefId']
                print('......checking CSA preset')
                csa_preset = get_object(
                    token=token,
                    objectId=csa_preset_id,
                )
                if csa_preset['objectLifeCycleStateId'] != 46871:
                    csa_is_incomplete = True
                    break
                print('......checking SRM preset')
                risks = get_related_objects(
                    token=token,
                    objectId=srm_preset_id,
                    relationshipTypeId=18899,
                )
                risk_externalRefIds = [risk['externalRefId'] for risk in risks]
                file_name = create_import_file(
                    srm_externalRefId=srm_external_refid,
                    risk_externalRefIds=risk_externalRefIds,
                )
                print('......moving SRM and risks complete')
                upload_file(
                    token=token,
                    file_name=file_name,
                )
            if csa_is_incomplete:
                print('CSA not completed, moving request to pending')
                message = 'CSA not completed, change request required'
                change_field(
                    token=token,
                    value=message,
                    objectId=request['id'],
                    fieldId=37048,
                )
                trigger_workflow(
                    token=token,
                    objectId=request['id'],
                    triggerId=75410,
                )
                print()
                continue
            print('...archiving site(s)')
            file_name = create_site_import_file(
                sites=sites,
            )
            upload_file(
                token=token,
                file_name=file_name,
            )
            completion_summary = []
            for site in sites:
                trigger_workflow(
                    token=token,
                    objectId=site['objectId'],
                    triggerId=25367,
                )
                site_name = site['objectName']
                completion_summary.append(
                    f'Site **{site_name}** has been archived along with its audits (if applicable)'
                )
            print('...adding completion summary')
            change_field(
                token=token,
                value='\n'.join(completion_summary),
                objectId=request['id'],
                fieldId=37048,
            )
            print('...archiving request')
            trigger_workflow(token, objectId=request['id'], triggerId=22578)
            print()
        print('End of script')