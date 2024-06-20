from dotenv import set_key, dotenv_values
from pathlib import Path
import os
import ruamel.yaml

env_file_path = Path(".env")
config_path = 'config.yml'
KEY_RECEEVI_DOMAIN = 'RECEEVI_DOMAIN'
KEY_SUPABASE_DOMAIN = 'SUPABASE_DOMAIN'
KEY_LETSENCRYPT_EMAIL = 'LETSENCRYPT_EMAIL'
KEY_LETSENCRYPT_TOS_ACCEPTED = 'LETSENCRYPT_TOS_ACCEPTED'

class TOSNotAccepted(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__("TOS Not accepted")

def read_file(filename: str):
    with open(filename, 'r') as file_obj:
        return file_obj.read()

def main():
    config = dotenv_values(".env")
    if 'your' in config['JWT_SECRET_KEY']:
        new_jwt_secret = os.urandom(32).hex()
        set_key(dotenv_path=env_file_path, key_to_set="JWT_SECRET_KEY", value_to_set=new_jwt_secret)
    if 'your' in config['WEBHOOK_VERIFY_TOKEN']:
        new_verify_token = os.urandom(32).hex()
        set_key(dotenv_path=env_file_path, key_to_set="WEBHOOK_VERIFY_TOKEN", value_to_set=new_verify_token)
    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    config_file_content = None
    try:
        config_yaml = read_file(config_path)
        config_file_content = yaml.load(config_yaml)
    except FileNotFoundError:
        config_file_content = {}
    # print(type(config_file_content))
    if KEY_RECEEVI_DOMAIN not in config_file_content:
        config_file_content[KEY_RECEEVI_DOMAIN] =  input("Enter receevi domain  (ex., receevi.exmaple.com) : ")
    if KEY_SUPABASE_DOMAIN not in config_file_content:
        config_file_content[KEY_SUPABASE_DOMAIN] = input("Enter supabase domain (ex., supabase.example.com): ")
    if KEY_LETSENCRYPT_EMAIL not in config_file_content:
        config_file_content[KEY_LETSENCRYPT_EMAIL] = input("Enter email address for let's encrypt: ")
    if KEY_LETSENCRYPT_TOS_ACCEPTED not in config_file_content:
        tos_accepted = input("Do you accept TOS of let's encrypt (https://community.letsencrypt.org/tos)? (Y/N) ")
        if tos_accepted in ('Y', 'y'):
            config_file_content[KEY_LETSENCRYPT_TOS_ACCEPTED] = True
        else:
            raise TOSNotAccepted()
    with open(config_path, 'w') as config_file:
        yaml.dump(config_file_content, config_file)

    set_key(dotenv_path=env_file_path, key_to_set="NEXT_PUBLIC_SUPABASE_URL", value_to_set=f'https://{config_file_content[KEY_SUPABASE_DOMAIN]}')


if __name__ == '__main__':
    main()
