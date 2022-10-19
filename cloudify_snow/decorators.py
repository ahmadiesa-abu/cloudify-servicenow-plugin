from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from functools import wraps

from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError

from .constants import TOKEN_AUTH_PATTEN


def with_auth(func):
    @wraps(func)
    def f(*args, **kwargs):
        ctx = kwargs['ctx']
        host = ctx.node.properties['client_config'].get('snow_host')
        username = ctx.node.properties['client_config'].get('snow_username')
        password = ctx.node.properties['client_config'].get('snow_password')
        client_id = ctx.node.properties['client_config'].get('snow_client_id')
        client_secret = ctx.node.properties['client_config'].get(
            'snow_client_secret')
        kwargs['snow_host'] = host
        if username and password:
            kwargs['snow_auth'] = HTTPBasicAuth(username, password)
        elif client_id and client_secret:
            oauth = OAuth2Session(
                client=LegacyApplicationClient(client_id=client_id))
            oauth.fetch_token(
                token_url=TOKEN_AUTH_PATTEN.format(host=host),
                client_id=client_id, client_secret=client_secret)
            kwargs['snow_auth'] = oauth
        else:
            raise NonRecoverableError("No valid authentication data provided.")
        return func(*args, **kwargs)
    return operation(f, resumable=True)
