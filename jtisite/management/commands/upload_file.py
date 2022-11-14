import requests
import random
import string

from time import sleep
from requests_toolbelt import MultipartEncoder


def upload_file(token, file_name):
    data = open(file_name, 'rb')
    fields = {
        'file': (
            file_name,
            data,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    }

    m = MultipartEncoder(
        fields=fields,
        boundary='----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters+string.digits, 16)))

    response = requests.post(
        'https://eu.core.resolver.com/creation/import',
        headers={
            'Connection': 'keep-alive',
            'Content-Type': m.content_type,
            'Authorization': f'bearer {token}',
        },
        params={
            'dryRun': 'false',
            'usingExternalRefIds': 'true',
            'deferPostProcessing': 'false',
        },
        data=m
    )
    response.raise_for_status()
    jobId = response.json()['jobId']

    print('......loading import file')
    
    status = 1
    while status == 1:
        response = requests.get(
            f'https://eu.core.resolver.com/object/job/{jobId}',
            headers={
                'Authorization': f'bearer {token}',
            },
        )
        response.raise_for_status()
        status = response.json()['status']
        if status == 1:
            print('.........additional 10 seconds for upload')
            sleep(10)
