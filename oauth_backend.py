from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv, set_key
import os

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
token_url = os.getenv('TOKEN_URL')
scope = os.getenv('SCOPE')


def get_bearer_token(client_id, client_secret, token_url, scope):
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope)
    write_to_env(token)
    print("Access token written to .env file successfully.")
    return token


def write_to_env(response_json):
    set_key('.env', 'ACCESS_TOKEN', response_json['access_token'])
    set_key('.env', 'REFRESH_TOKEN', response_json['refresh_token'])
    set_key('.env', 'EXPIRES_IN', str(response_json['expires_in']))


get_bearer_token(client_id, client_secret, token_url, scope)
