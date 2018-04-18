from __future__ import print_function
import os
import sys
import json
import requests

"""
The script needs an Globus Auth Client ID and Secret 
to create a child Globus Auth Client with dependent_token
grant type and a resource server scope. The dependent_token
grant type is neccessary to exchange an eccess token sent 
by a web app to the resource server to dependent access
token that can be used by the resource server to access
Globus services (e.g. Transfer API).
Please go to https://developers.globus.org to create a project
and a Globus Auth client, and paste a client id and a secret
below. Specify also a DNS name of the resource server.
"""

CLIENT_ID = '<Globus Auth Client ID>'
CLIENT_SECRET = '<Globus Auth Client Secret>'
DNS_NAME = 'drf.example.com'
redirect_uri = 'https://{}/redirect'.format(DNS_NAME)
dependent_scope = 'urn:globus:auth:scope:transfer.api.globus.org:all'


def get_dependent_scope(dependent_scope_string):
    """ Gets UUID of the scope """
    print('Get a UUID of the dependent scope: {}'.format(dependent_scope_string))
    path = '/v2/api/scopes?scope_strings={}'.format(dependent_scope_string)
    print('GET {}'.format(path))
    r = requests.get(
            'https://auth.globus.org{}'.format(path),
            auth=(CLIENT_ID, CLIENT_SECRET)
    )
    rj = r.json()
    print(json.dumps(rj, indent=4))
    dependent_scope_uuid = rj['scopes'][0]['id']
    print('Dependent scope UUID: {}'.format(dependent_scope_uuid))
    return dependent_scope_uuid


def create_client(project_uuid, redirect_uri):
    """ Create a child client with dependent_token grant_type """
    print('Create a new child client')
    path = '/v2/api/clients'
    print('POST {}'.format(path))
    r = requests.post(
            'https://auth.globus.org{}'.format(path),
            data=json.dumps({
                'client': {
                    'name': 'Resource Server on {}'.format(DNS_NAME),
                    'public_client': False,
                    'project': project_uuid,
                    'redirect_uris': [
                        redirect_uri
                    ]
                }
            }),
            auth=(CLIENT_ID, CLIENT_SECRET)
    )
    rj = r.json()
    print(json.dumps(rj, indent=4))
    client_id = rj['client']['id']
    print('DRF client_id: {}'.format(client_id))
    print('Use this client_id with the secret of the parent client secret {}'.format(CLIENT_SECRET))
    return client_id


def create_scope(client_uuid, dependent_scope_uuid):
    """ Create a new scope with the dependent scope."""
    print('Create a new scope with the dependent scope: {}'.format(dependent_scope_uuid))
    path = '/v2/api/clients/{}/scopes'.format(client_uuid)
    print('POST {}'.format(path))
    r = requests.post(
            'https://auth.globus.org{}'.format(path),
            data=json.dumps({
                'scope': {
                    'name': 'Access the Globus Transfer Service on behalf of you',
                    'description': 'If allowed, the web application will be able to access your Globus endpoints, submit transfers, list transfer jobs, manage your endpoints, etc',
                    'scope_suffix': 'all',
                    'dependent_scopes': [
                        {
                            'scope': dependent_scope_uuid,
                            'optional': False,
                            'requires_refresh_token': False
                        }
                    ]
                }
            }),
            auth=(client_uuid, CLIENT_SECRET)
    )
    rj = r.json()
    print(json.dumps(rj, indent=4))
    scope_id = rj['scopes'][0]['id']
    scope_string = rj['scopes'][0]['scope_string']
    print('Resource server scope string: {}'.format(scope_string))
    return scope_id


def update_client(client_uuid, scope_uuid):
    """Add scope and redirect_uri to the client"""
    print('Update client: {}'.format(client_uuid))
    path = '/v2/api/clients/{}'.format(client_uuid)
    print('PUT {}'.format(path))
    r = requests.put(
            'https://auth.globus.org{}'.format(path),
            data=json.dumps({
                'client': {
                    'scopes': [
                        scope_uuid
                    ]
                }
            }),
            auth=(CLIENT_ID, CLIENT_SECRET)
    )
    rj = r.json()
    print(json.dumps(rj, indent=4))


def get_project(client_uuid):
    """ Get a UUID of the client project """
    print('Get a UUID of the parent client project')
    path = '/v2/api/clients/{}'.format(client_uuid)
    print('GET {}'.format(path))
    r = requests.get(
            'https://auth.globus.org{}'.format(path),
            auth=(CLIENT_ID, CLIENT_SECRET)
    )
    rj = r.json()
    print(json.dumps(rj, indent=4))
    project_uuid = rj['client']['project']
    print('Project UUID: {}'.format(project_uuid))
    return project_uuid


def delete_client(client_uuid):
    """Delete the client"""
    print('Delete client: {}'.format(client_uuid))
    path = '/v2/api/clients/{}'.format(client_uuid)
    print('DELETE {}'.format(path))
    r = requests.delete(
            'https://auth.globus.org{}'.format(path),
            auth=(CLIENT_ID, CLIENT_SECRET)
    )
    rj = r.json()
    print(json.dumps(rj, indent=4))


def list_clients():
    print('List all clients')
    path = '/v2/api/clients'
    print('GET {}'.format(path))
    r = requests.get(
            'https://auth.globus.org{}'.format(path),
            auth=(CLIENT_ID, CLIENT_SECRET)
    )
    print(json.dumps(r.json(), indent=4))


def list_scopes():
    print('List all scopes')
    path = '/v2/api/scopes'
    print('GET {}'.format(path))
    r = requests.get(
            'https://auth.globus.org{}'.format(path),
            auth=(CLIENT_ID, CLIENT_SECRET)
    )
    print(json.dumps(r.json(), indent=4))


def main():
    dependent_scope_uuid = get_dependent_scope(dependent_scope)
    project_uuid = get_project(CLIENT_ID)
    client_uuid = create_client(project_uuid, redirect_uri)
    scope_uuid = create_scope(client_uuid, dependent_scope_uuid)
    #update_client(client_uuid, scope_uuid, redirect_uri)
    #delete_client('cd1eefe5-9410-41da-a185-3b4f4d88b3c0')

    list_clients()
    list_scopes()


if __name__ == '__main__':
    print('Parent client ID: {}'.format(CLIENT_ID))
    main()

