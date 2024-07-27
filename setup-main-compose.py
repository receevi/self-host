import ruamel.yaml
from ruamel.yaml.scalarstring import LiteralScalarString
import textwrap

config_path = 'config.yml'
docker_compose_file_location = 'docker-compose.yml'
KEY_PRODUCT_NAME = 'PRODUCT_NAME'

def LS(s):
    return LiteralScalarString(textwrap.dedent(s))

def read_file(filename: str):
    with open(filename, 'r') as file_obj:
        return file_obj.read()

def write_file(filename: str, content: str):
    with open(filename, 'w') as file_obj:
        file_obj.write(content)

def read_config():
    config_yaml = read_file(config_path)
    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml.load(config_yaml)

def setup_docker_compose(app_config):
    docker_compose_yaml = read_file(docker_compose_file_location)
    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    compose_file_content = yaml.load(docker_compose_yaml)
    product_name = app_config[KEY_PRODUCT_NAME]
    compose_file_content['name'] = product_name
    compose_file_content['services']['receevi']['container_name'] = f'{product_name}-receevi'
    with open(docker_compose_file_location, 'w') as compose_file:
        yaml.dump(compose_file_content, compose_file)

def main():
    app_config = read_config()
    setup_docker_compose(app_config)

if __name__ == '__main__':
    main()
