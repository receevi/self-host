from dotenv import set_key, dotenv_values
from pathlib import Path
import os

env_file_path = Path(".env")

def main():
    config = dotenv_values(".env")
    if 'your' in config['JWT_SECRET_KEY']:
        new_jwt_secret = os.urandom(32).hex()
        set_key(dotenv_path=env_file_path, key_to_set="JWT_SECRET_KEY", value_to_set=new_jwt_secret)
    if 'your' in config['WEBHOOK_VERIFY_TOKEN']:
        new_verify_token = os.urandom(32).hex()
        set_key(dotenv_path=env_file_path, key_to_set="WEBHOOK_VERIFY_TOKEN", value_to_set=new_verify_token)


if __name__ == '__main__':
    main()

