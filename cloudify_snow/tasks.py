import json

from requests import Request, Session
from requests import RequestException, ConnectionError, HTTPError

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError

from .constants import TABLE_API_PATTERN
from .decorators import with_auth


@with_auth
def list_request_items(ctx, snow_host, snow_auth, **kwargs):
    # establish the connection
    url = TABLE_API_PATTERN.format(host=snow_host, table_name="sc_req_item")
    method = "GET"
    headers = {"Content-Type":"application/json", "Accept":"application/json"}
    req = Request(method,
                  url,
                  headers=headers,
                  auth=snow_auth)

    prepped = req.prepare()
    session = Session()

    try:
        response = session.send(prepped)
    except (RequestException, ConnectionError, HTTPError) as e:
        raise NonRecoverableError('Exception raised: {0}'.format(str(e)))

    result = {
        'status_code': response.status_code,
        'body': response.request.body,
        'content': response.content
    }

    if not response.ok:
        raise NonRecoverableError('Request failed: {0}'.format(result))

    #ctx.logger.info('Request OK: {0}'.format(result))

    # setting node instance runtime property
    result = json.loads(result.get('content', {})).get('result', [])
    ritems = []
    for ritem in result:
        ritems.append(ritem.get('number'))
    ctx.instance.runtime_properties['requested_items'] = ritems


@with_auth
def create_ci(ctx, snow_host, snow_auth, **kwargs):
    table_name = ''
    ctx.logger.info('node_type : {0}'.format(ctx.node.type))
    if ctx.node.type == 'cloudify.nodes.snow.linux_server':
        table_name = 'cmdb_ci_linux_server'
    elif ctx.node.type == 'cloudify.nodes.snow.unix_server':
        table_name = 'cmdb_ci_unix_server'
    elif ctx.node.type == 'cloudify.nodes.snow.windows_server':
        table_name = 'cmdb_ci_win_server'
    elif ctx.node.type == 'cloudify.nodes.snow.server':
        table_name = 'cmdb_ci_server'
    url = TABLE_API_PATTERN.format(host=snow_host, table_name=table_name)
    method = "POST"
    headers = {"Content-Type":"application/json", "Accept":"application/json"}
    # payload = {
    #     'cpu_count': '1',
    #     'dns_domain': 'domain.com',
    #     'install_status': 'Installed',
    #     'ip_address': '1.1.1.1',
    #     'manufacturer': 'Virtual',
    #     'model_number': 'Virtual',
    #     'name': 'some-server',
    #     'ram': '2048',
    #     'serial_number': 'Virtual',
    #     'short_description': 'some description for {0}'.format(table_name)
    # }
    payload = ctx.node.properties.get('resource_config', {})
    req = Request(method,
                  url,
                  json=payload,
                  headers=headers,
                  auth=snow_auth)

    prepped = req.prepare()
    session = Session()

    try:
        response = session.send(prepped)
    except (RequestException, ConnectionError, HTTPError) as e:
        raise NonRecoverableError('Exception raised: {0}'.format(str(e)))

    result = {
        'status_code': response.status_code,
        'body': response.request.body,
        'content': response.content
    }

    if not response.ok:
        raise NonRecoverableError('Request failed: {0}'.format(result))
    ctx.logger.info('Request OK: {0}'.format(result))
