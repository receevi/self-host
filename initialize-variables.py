from common import KEY_FACEBOOK_APP_SECRET, KEY_HTTP_PORT, KEY_HTTPS_PORT, KEY_LETSENCRYPT_EMAIL, KEY_LETSENCRYPT_TOS_ACCEPTED, KEY_PRODUCT_NAME, KEY_RECEEVI_DOMAIN, KEY_SETUP_HTTPS, KEY_SUPABASE_DOMAIN, KEY_WHATSAPP_ACCESS_TOKEN, KEY_WHATSAPP_API_PHONE_NUMBER_ID, KEY_WHATSAPP_BUSINESS_ACCOUNT_ID
from dotenv import set_key, dotenv_values
from pathlib import Path
import os
import ruamel.yaml

env_file_path = Path(".env")
config_path = 'config.yml'

facebook_app_secret_instructions = """


Facebook app secret

1. Go to https://developers.facebook.com/apps/
2. Choose your app
3. Go to App settings > Basic
4. Get App secret

App secret: """

whatsapp_permanent_access_token = """

Follow this popular stackoverflow answer to generate permanent token - https://stackoverflow.com/a/74253066

Token: """

phone_number_id_instructions = """

1. Go to https://developers.facebook.com/apps/
2. Choose your app
3. Go to WhatsApp > API Setup
3. Copy "Phone number ID"
4. Copy "WhatsApp Business Account ID"

Phone number ID: """

whatsapp_business_account_id_instructions = """WhatsApp Business Account ID: """

class TOSNotAccepted(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__("TOS Not accepted")

class InvalidYN(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__("Response should be either Y or N")

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
    if KEY_PRODUCT_NAME not in config_file_content:
        config_file_content[KEY_PRODUCT_NAME] =  input("Enter product / company name without space all small characters (ex., examplecompany) : ")
    if KEY_RECEEVI_DOMAIN not in config_file_content:
        config_file_content[KEY_RECEEVI_DOMAIN] =  input("Enter receevi domain  (ex., receevi.exmaple.com) : ")
    if KEY_SUPABASE_DOMAIN not in config_file_content:
        config_file_content[KEY_SUPABASE_DOMAIN] = input("Enter supabase domain (ex., supabase.example.com): ")
    if KEY_LETSENCRYPT_EMAIL not in config_file_content:
        config_file_content[KEY_LETSENCRYPT_EMAIL] = input("Enter email address for let's encrypt: ")
    if KEY_FACEBOOK_APP_SECRET not in config_file_content:
        config_file_content[KEY_FACEBOOK_APP_SECRET] = input(facebook_app_secret_instructions)
    if KEY_WHATSAPP_ACCESS_TOKEN not in config_file_content:
        config_file_content[KEY_WHATSAPP_ACCESS_TOKEN] = input(whatsapp_permanent_access_token)
    if KEY_WHATSAPP_API_PHONE_NUMBER_ID not in config_file_content:
        config_file_content[KEY_WHATSAPP_API_PHONE_NUMBER_ID] = input(phone_number_id_instructions)
    if KEY_WHATSAPP_BUSINESS_ACCOUNT_ID not in config_file_content:
        config_file_content[KEY_WHATSAPP_BUSINESS_ACCOUNT_ID] = input(whatsapp_business_account_id_instructions)

    if KEY_HTTP_PORT not in config_file_content:
        http_port_text = input("http port (default. 80): ")
        if http_port_text.strip() == '':
            config_file_content[KEY_HTTP_PORT] = 80
        else:
            config_file_content[KEY_HTTP_PORT] = int(http_port_text)

    if KEY_HTTPS_PORT not in config_file_content:
        https_port_text = input("https port (default. 443): ")
        if https_port_text.strip() == '':
            config_file_content[KEY_HTTPS_PORT] = 443
        else:
            config_file_content[KEY_HTTPS_PORT] = int(https_port_text)

    if KEY_SETUP_HTTPS not in config_file_content:
        tos_accepted = input("Do you want to setup HTTPS using let's encrypt? (Y/N) ")
        if tos_accepted in ('Y', 'y'):
            config_file_content[KEY_SETUP_HTTPS] = True
        if tos_accepted in ('N', 'n'):
            config_file_content[KEY_SETUP_HTTPS] = False
        else:
            raise InvalidYN()
    if config_file_content[KEY_SETUP_HTTPS] and KEY_LETSENCRYPT_TOS_ACCEPTED not in config_file_content:
        tos_accepted = input("Do you accept TOS of let's encrypt (https://community.letsencrypt.org/tos)? (Y/N) ")
        if tos_accepted in ('Y', 'y'):
            config_file_content[KEY_LETSENCRYPT_TOS_ACCEPTED] = True
        else:
            raise TOSNotAccepted()
    with open(config_path, 'w') as config_file:
        yaml.dump(config_file_content, config_file)

    set_key(dotenv_path=env_file_path, key_to_set="NEXT_PUBLIC_SUPABASE_URL", value_to_set=f'https://{config_file_content[KEY_SUPABASE_DOMAIN]}')
    set_key(dotenv_path=env_file_path, key_to_set=KEY_FACEBOOK_APP_SECRET, value_to_set=config_file_content[KEY_FACEBOOK_APP_SECRET])
    set_key(dotenv_path=env_file_path, key_to_set=KEY_WHATSAPP_ACCESS_TOKEN, value_to_set=config_file_content[KEY_WHATSAPP_ACCESS_TOKEN])
    set_key(dotenv_path=env_file_path, key_to_set=KEY_WHATSAPP_API_PHONE_NUMBER_ID, value_to_set=config_file_content[KEY_WHATSAPP_API_PHONE_NUMBER_ID])
    set_key(dotenv_path=env_file_path, key_to_set=KEY_WHATSAPP_BUSINESS_ACCOUNT_ID, value_to_set=config_file_content[KEY_WHATSAPP_BUSINESS_ACCOUNT_ID])


if __name__ == '__main__':
    main()
