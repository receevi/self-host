import re
import os
from dotenv import set_key, dotenv_values, load_dotenv
from pathlib import Path
import os
import jwt
import datetime
import copy
import ruamel.yaml
from ruamel.yaml.scalarstring import LiteralScalarString
import sys, textwrap

load_dotenv()

supabase_docker_compose_file_location = 'supabase/docker/docker-compose.yml'
kong_file_location = 'supabase/docker/volumes/api/kong.yml'
prefunction = """
local scheme = kong.request.get_scheme()
local path = kong.request.get_path()
  if scheme == 'http' and not string.match(path, 'acme%-challenge') then
  local host = kong.request.get_host()
  local query = kong.request.get_path_with_query()
  local url = 'https://' .. host .. query
  kong.response.set_header('Location',url)
  return kong.response.exit(302,url)
end
""".strip()

def LS(s):
    return LiteralScalarString(textwrap.dedent(s))

def read_file(filename: str):
    with open(filename, 'r') as file_obj:
        return file_obj.read()

def write_file(filename: str, content: str):
    with open(filename, 'w') as file_obj:
        file_obj.write(content)

def setup_docker_compose():
    docker_compose_yaml = read_file(supabase_docker_compose_file_location)
    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    compose_file_content = yaml.load(docker_compose_yaml)
    function_environments = compose_file_content['services']['functions']['environment']
    if 'WHATSAPP_ACCESS_TOKEN' not in function_environments:
        function_environments['WHATSAPP_ACCESS_TOKEN'] = os.getenv('WHATSAPP_ACCESS_TOKEN')
    if 'WHATSAPP_API_PHONE_NUMBER_ID' not in function_environments:
        function_environments['WHATSAPP_API_PHONE_NUMBER_ID'] = os.getenv('WHATSAPP_API_PHONE_NUMBER_ID')
    if 'WHATSAPP_BUSINESS_ACCOUNT_ID' not in function_environments:
        function_environments['WHATSAPP_BUSINESS_ACCOUNT_ID'] = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')

    kong_env_vars = compose_file_content['services']['kong']['environment']
    if 'acme' not in kong_env_vars['KONG_PLUGINS']:
        kong_env_vars['KONG_PLUGINS'] = kong_env_vars['KONG_PLUGINS'] + ',acme'
    if 'pre-function' not in kong_env_vars['KONG_PLUGINS']:
        kong_env_vars['KONG_PLUGINS'] = kong_env_vars['KONG_PLUGINS'] + ',pre-function'
    if 'KONG_LUA_SSL_TRUSTED_CERTIFICATE' not in kong_env_vars:
        kong_env_vars['KONG_LUA_SSL_TRUSTED_CERTIFICATE'] = '/etc/ssl/certs/ca-certificates.crt'
    if 'KONG_NGINX_PROXY_LUA_SSL_TRUSTED_CERTIFICATE' not in kong_env_vars:
        kong_env_vars['KONG_NGINX_PROXY_LUA_SSL_TRUSTED_CERTIFICATE'] = '/etc/ssl/certs/ca-certificates.crt'
    with open(supabase_docker_compose_file_location, 'w') as compose_file:
        yaml.dump(compose_file_content, compose_file)

def setup_env_vars():
    env_file_path = Path("supabase/docker/.env")
    config = dotenv_values("supabase/docker/.env")
    if 'your' in config['JWT_SECRET']:
        set_key(dotenv_path=env_file_path, key_to_set="JWT_SECRET", value_to_set=os.getenv('JWT_SECRET_KEY'))
    if 'your' in config['POSTGRES_PASSWORD']:
        set_key(dotenv_path=env_file_path, key_to_set="POSTGRES_PASSWORD", value_to_set=os.urandom(8).hex())
    if 'this_password_is_insecure_and_should_be_updated' in config['DASHBOARD_PASSWORD']:
        set_key(dotenv_path=env_file_path, key_to_set="DASHBOARD_PASSWORD", value_to_set=os.urandom(32).hex())
    set_key(dotenv_path=env_file_path, key_to_set="STUDIO_DEFAULT_ORGANIZATION", value_to_set='Receevi')
    set_key(dotenv_path=env_file_path, key_to_set="STUDIO_DEFAULT_PROJECT", value_to_set='Receevi')
    set_key(dotenv_path=env_file_path, key_to_set="KONG_HTTP_PORT", value_to_set='80')
    set_key(dotenv_path=env_file_path, key_to_set="KONG_HTTPS_PORT", value_to_set='443')

    current_time = datetime.datetime.now()
    epx_time = current_time + datetime.timedelta(days= 5 * 365.25)

    base_payload = {
        "iss": "supabase",
        "iat": int(round(current_time.timestamp())),
        "exp": int(round(epx_time.timestamp()))
    }

    if config['ANON_KEY'] == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE':
        anon_payload = copy.deepcopy(base_payload)
        anon_payload['role'] = "anon"
        anon_key = jwt.encode(anon_payload, os.getenv('JWT_SECRET_KEY'), algorithm="HS256")
        set_key(dotenv_path=env_file_path, key_to_set="ANON_KEY", value_to_set=anon_key)
        set_key(dotenv_path='.env', key_to_set="NEXT_PUBLIC_SUPABASE_ANON_KEY", value_to_set=anon_key)

    if config['SERVICE_ROLE_KEY'] == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJzZXJ2aWNlX3JvbGUiLAogICAgImlzcyI6ICJzdXBhYmFzZS1kZW1vIiwKICAgICJpYXQiOiAxNjQxNzY5MjAwLAogICAgImV4cCI6IDE3OTk1MzU2MDAKfQ.DaYlNEoUrrEn2Ig7tqibS-PHK5vgusbcbo7X36XVt4Q':
        service_payload = copy.deepcopy(base_payload)
        service_payload['role'] = "service_role"
        service_key = jwt.encode(service_payload, os.getenv('JWT_SECRET_KEY'), algorithm="HS256")
        set_key(dotenv_path=env_file_path, key_to_set="SERVICE_ROLE_KEY", value_to_set=service_key)
        set_key(dotenv_path='.env', key_to_set="SUPABASE_SERVICE_ROLE", value_to_set=service_key)

def setup_kong():
    kong_yaml = read_file(kong_file_location)
    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    kong_file_content = yaml.load(kong_yaml)

    receevi_service_present_at = -1

    receevi_kong_service = {
        'name': 'receevi',
        'url': 'http://receevi:3000/',
        'routes': [
            {
                'name': 'receevi-all',
                'strip_path': True,
                'paths': ['/'],
                'hosts': ['local.receevi.com']
            }
        ]
    }

    for index, service in enumerate(kong_file_content['services']):
        if service['name'] == 'receevi':
            receevi_service_present_at = index
        else:
            for route in service['routes']:
                route['hosts'] = ['local-supabase.receevi.com']

    if receevi_service_present_at == -1:
        kong_file_content['services'].append(receevi_kong_service)
    else:
        kong_file_content['services'][index] = receevi_kong_service

    if 'plugins' not in kong_file_content:
        kong_file_content['plugins'] = []

    acme_plugin_present = False
    prefunction_plugin_present = False

    acme_plugin = {
        'name': 'acme',
        'config': {
            'account_email': 'hello@test.com',
            'tos_accepted': True,
            'domains': [
                'local.receevi.com',
                'local-supabase.receevi.com',
            ]
        }
    }

    prefunction_plugin = {
        'name': 'pre-function',
        'config': {
            'access': [LS(prefunction)]
        }
    }

    for index, plugin in enumerate(kong_file_content['plugins']):
        if plugin['name'] == 'acme':
            kong_file_content['plugins'][index] = acme_plugin
            acme_plugin_present = True
        if plugin['name'] == 'pre-function':
            kong_file_content['plugins'][index] = prefunction_plugin
            prefunction_plugin_present = True

    if not acme_plugin_present:
        kong_file_content['plugins'].append(acme_plugin)

    if not prefunction_plugin_present:
        kong_file_content['plugins'].append(prefunction_plugin)

    with open(kong_file_location, 'w') as kong_file:
        yaml.dump(kong_file_content, kong_file)

def main():
    setup_docker_compose()
    setup_env_vars()
    setup_kong()

if __name__ == '__main__':
    main()
