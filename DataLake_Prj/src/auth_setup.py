from authlib.integrations.requests_client import OAuth2Session
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

TENENT_ID = os.getenv('ti')
TOKEN_ENDPOINT = os.getenv('pu') + os.getenv('ot')
CLIENT_ID = os.getenv('ci')
CLIENT_SECRET = os.getenv('cs')
USERNAME = os.getenv('saak')
PASSWORD = os.getenv('sask')
MINGLE_ENDPOINT = os.getenv('iu')

# AUTHENTICATION - GENERATE ACCESS TOKEN
class AuthSetup:
    client:OAuth2Session
    def __init__(self, access_token=None, expires_at=None):
        if access_token and expires_at:
            self.access_token=access_token
            self.expires_at=expires_at
        else:
            # COMMENT FOR WHILE
            self.client = OAuth2Session(CLIENT_ID, CLIENT_SECRET,token_endpoint=TOKEN_ENDPOINT)
            self.me = MINGLE_ENDPOINT
            self.ti = TENENT_ID
            self.fetch_access_token()

    def time_left(self):
        hr = int((self.expires_at - int(datetime.now().timestamp()))/3600)
        min_ = int((self.expires_at - int(datetime.now().timestamp()))/60) - hr*60
        return f"{hr} h {min_} min "
        
    def fetch_access_token(self):
        resp = self.client.fetch_access_token(username=USERNAME, password=PASSWORD, grant_type='password')
        self.access_token=resp['access_token']
        self.refresh_token=resp['refresh_token']
        self.token_type=resp['token_type']
        self.expires_in=resp['expires_in']
        self.expires_at:int=resp['expires_at']
        # print(resp)

    def fetch_refresh_token(self):
        if self.access_token:
            if (int(datetime.now().timestamp()) > self.expires_at):
                self.fetch_access_token()
