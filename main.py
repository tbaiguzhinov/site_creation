import os
import requests

from dotenv import load_dotenv


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


def main():
    load_dotenv()

    # Authentication
    token = authenticate(
        login=os.getenv('EMAIL'),
        password=os.getenv('PASSWORD'),
    )
    print(token)


if __name__ == '__main__':
    main()
