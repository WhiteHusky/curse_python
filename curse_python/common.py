import requests
from .exceptions import RequestException
# API DOC: https://twitchappapi.docs.apiary.io/
BASE_URL = 'https://addons-ecs.forgesvc.net/api/v2'
BASE_HEADERS = {
    'user-agent': 'curse-python/0.0.1'
}


def table_merge(table_a, table_b):
    assert type(table_a) == 'table' and type(table_b) == 'table'
    for key, value in table_b.items():
        table_a[key] = value
    return table_a

def handle_headers(kargs):
    headers = BASE_HEADERS
    if 'headers' in kargs:
        table_merge(headers, kargs['headers'])
        del kargs['headers']
    return headers

def get_request(path, **kargs):
    headers = handle_headers(kargs)
    response = requests.get(BASE_URL + path, headers=headers, **kargs)
    if response.status_code != 200:
        raise RequestException(response.status_code)
    return response.json()