import os

from dotenv import load_dotenv
from jtisite.management.commands.resolver_api import search_objects, authenticate, create_new_site, get_all_sites


SYMBOLS = {
    'factory': {'symbol': '🏭', 'char': chr(127981)},
    'leaf': {'symbol': '🍂', 'char': chr(127810)},
    'box': {'symbol': '📦', 'char': chr(128230)},
    'cigarette': {'symbol': '🚬', 'char': chr(128684)},
    'office': {'symbol': '🏠', 'char': chr(127968)},
}

request_type_id = 8063
request_active = 31056
request_type_field = 42977
site_create_request = 122005


def main():
    load_dotenv()

    token = authenticate(
        login=os.getenv('EMAIL'),
        password=os.getenv('PASSWORD'),
    )
    get_all_sites(token)
    return
    # new_requests = []
    # open_requests = search_objects(
    #     token=token,
    #     objectTypeId=request_type_id,
    #     lifeCycleId=request_active,
    # )
    # for request in open_requests:
    #     request_type = request['evaluations'][str(request_type_field)]['value'] if str(
    #         request_type_field) in request['evaluations'] else None
    #     if request['objectLifeCycleStateId'] == request_active and request_type == site_create_request:
    #         new_requests.append(request)
    new_requests = [{'id': 1439566, 'name': 'Medium priority request #2022-620: JTI Site: add new  ', 'description': 'Warehouse for the storage of all POSM material', 'externalRefId': 'f54b5030-1c5d-4a36-a896-fee6f95c7b33', 'uniqueId': '620', 'objectTypeId': 8063, 'evaluations': {'37037': {'value': None}, '37042': {'value': None}, '37048': {'value': None}, '37052': {'value': 97861}, '37055': {'value': 0}, '37064': {'value': None}, '37083': {'value': 98204}, '37085': {'value': None}, '37090': {'value': 0}, '37091': {'value': [{'id': 27102, 'displayFileName': 'PHOTO-2022-10-13-13-27-57 (3).jpg'}, {'id': 27103, 'displayFileName': 'PHOTO-2022-10-13-13-27-58 (1).jpg'}, {'id': 27104, 'displayFileName': 'PHOTO-2022-10-13-13-27-58 (2).jpg'}, {'id': 27105, 'displayFileName': 'PHOTO-2022-10-13-13-27-58.jpg'}]}, '37093': {'value': 97832}, '37095': {'value': None}, '37098': {'value': 97796}, '37103': {'value': 0}, '37125': {'value': None}, '37128': {'value': None}, '40607': {'value': 0}, '40608': {'value': 0}, '40609': {'value': None}, '40610': {'value': None}, '40611': {'value': None}, '40612': {'value': 86}, '40613': {'value': 115000}, '40615': {'value': 115447}, '42977': {'value': 122005}, '51531': {'value': None}, '51551': {'value': 1357084800}, '51565': {'value': {'x': 0, 'y': 0, 'name': 'PHOTO-2022-10-13-13-27-57.jpg', 'width': 0, 'height': 0, 'cropped': 0, 'original': 27100, 'compressed': 27101, 'description': ''}}, '51620': {'value': 'No. 1 Awosika Avenue, Ikeja Industrial Estate, Ikeja, Lagos.'}, '52410': {'value': None}, '54124': {'value': None}, '61157': {'value': None}}, 'formulas': {}, 'objectLifeCycleStateId': 31056, 'created': '2022-11-02T07:44:51.718Z', 'createdBy': 2965, 'modified': '2022-11-02T07:44:51.993Z', 'modifiedBy': 2965, 'dateStateChanged': '2022-11-02T07:44:52.284Z', 'assessment': False, 'anchor': None, 'dimensions': [], 'uniqueIdArray': [620], 'assessmentObjectId': None, 'assessmentObjectTypeId': None, 'assessmentLaunched': None, 'last_trigger_time': '2022-11-02T07:44:52.142Z', 'is_archive': False, 'geolocation': {'id': 42655, 'geo': {'type': 'Point', 'coordinates': [6.61166191, 3.339634539]}, 'country': 'NGA', 'countryName': 'Nigeria', 'state': '', 'stateName': 'Lagos', 'city': 'Lagos', 'zipCode': '', 'street': 'Awosika Ave', 'houseNumber': '', 'notes': '', 'created': '2022-11-02T07:44:50.874Z', 'label': 'Awosika Ave, Ikeja, Nigeria'}, 'geolocation_id': 42655, 'lastSyncDate': None, 'submitter': None, 'submitterName': None, 'submitterType': None, 'creationType': None, 'isSubmitterAnonymous': False, 'hasSubmitterOptedIn': False, 'creationEmailAddressId': None, 'canWrite': False, 'elasticScore': 3}]

    for request in new_requests:
        site_id = create_new_site(token, request)

    # Link site to country
    # Link site to region

# Create Assessment
# {"name":"📦Almaty, Kazakhstan: M&S WH cat. C (TEST)","objectTypeId":11307,"relationships":[{"relationshipId":18898,"value":[1437147]},{"relationshipId":18892,"value":[304126]}],"references":[],"evaluations":[{"fieldId":51533,"value":149233}],"files":[],"assessment":true,"dimensions":[{"type":1,"optionId":1437147,"dimensionId":8100}],"triggerId":38480,"parent":{"inverse":true,"objectId":1437147,"relationshipTypeId":18898},"tz":"Asia/Almaty"}

# Add presets
# https://eu.core.resolver.com/creation/assessment/1437148/focus
# {"objectId": 304124}
# https://eu.core.resolver.com/creation/assessment/1437148/focus
# {"objectId":304125}

# Confirm scope
# https://eu.core.resolver.com/creation/assessment/1437148/launch?useJob=true
# {}
# Returns Job number
# sleep?
# May fail

# Confirm scope
# POST https://eu.core.resolver.com/data/object/1437148/trigger/38600/go?tz=Asia/Almaty

# Change names for CS Audit and for SRM
# for SRM link all Risks to County and update description

# for CS Audit =  Applicability


# End of Script
if __name__ == '__main__':
    main()
