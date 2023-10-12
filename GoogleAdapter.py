from authlib.integrations.flask_client import OAuth
from flask import session, url_for, current_app
import os
from BaseAdapter import BaseAdapter
from dotenv import load_dotenv

load_dotenv()

class GoogleAdapter(BaseAdapter):

    _CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    _CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    _AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
    _ACCESS_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    _REFRESH_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    _SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    _OAUTH_SUCCESS_ROUTE = '/google/oauth/success'
    _TOKEN_EXCHANGE_SUCCESS_ROUTE = '/google/token/success'
    _MAIL_API_URL = 'https://www.googleapis.com/gmail/v1/users/me/messages'
    _SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


    def __init__(self, oauthConnector):
        self.name = "google"
        super().__init__(oauthConnector)

    def query_email_provider(self, since):
        query = f'after:{since}'
        return  self.oauth.google.get(
                    self._MAIL_API_URL,
                    params = {  'q': query,
                                'maxResults': 1
                    }, 
                    token = session['token']
                )


    def search_emails(self, since):
        resp = self.query_email_provider(since)
        messages = resp.json().get('messages', [])
        return str(len(messages) > 0)

    
