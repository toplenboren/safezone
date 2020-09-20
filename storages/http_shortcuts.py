# Shortcuts for http requests
import requests


def _get_token_header(t: str) -> dict:
    return {'Authorization': 'OAuth ' + t}


def get_with_OAuth(addr: str, params: dict = {}, token: str = ''):
    return requests.get(addr, params=params, headers=_get_token_header(token))


def post_with_OAuth(addr: str, data: dict = {}, token: str = ''):
    return requests.post(addr, data=data, headers=_get_token_header(token))
