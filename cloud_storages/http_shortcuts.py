# Shortcuts for http requests
import requests


def _get_token_header(t: str) -> dict:
    return {'Authorization': 'OAuth ' + t}


def get_with_OAuth(addr: str, params: dict = {}, token: str = '', **kwargs):
    return requests.get(addr, params=params, headers=_get_token_header(token), **kwargs)


def post_with_OAuth(addr: str, data: dict = {}, token: str = '', **kwargs):
    return requests.post(addr, data=data, headers=_get_token_header(token), **kwargs)


def put_with_OAuth(addr: str, token: str = '', **kwargs):
    return requests.put(addr, headers=_get_token_header(token), **kwargs)


def patch_with_OAuth(addr: str, token: str = '', **kwargs):
    return requests.patch(addr, headers=_get_token_header(token), **kwargs)
