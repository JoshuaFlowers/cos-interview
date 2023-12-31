from authlib.integrations.flask_client import OAuth
from datetime import datetime
from flask import session, url_for, current_app, abort
import os
from BaseAdapter import BaseAdapter
from dotenv import load_dotenv

load_dotenv()

class MicrosoftAdapter(BaseAdapter):

    _CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID')
    _CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET')
    _AUTH_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize'
    _ACCESS_TOKEN_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token'
    _REFRESH_TOKEN_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token'
    _SCOPES = ['Mail.Read']
    _OAUTH_SUCCESS_ROUTE = '/microsoft/oauth/success'
    _TOKEN_EXCHANGE_SUCCESS_ROUTE = '/microsoft/token/success'
    _MAIL_API_URL = 'https://graph.microsoft.com/v1.0/me/messages'


    def __init__(self, oauthConnector):
        self.name = "microsoft"
        super().__init__(oauthConnector)

    def query_email_provider(self, query):
        return self.oauth.microsoft.get(
                    self._MAIL_API_URL,
                    params = {  '$filter': query,
                                '$count': 'true',
                                '$select': 'receivedDateTime', 
                                '$top': 1 
                    },
                    token = session['token']
                )

    def search_emails(self, since):
        timestamp = None
        try:
            timestamp = datetime.utcfromtimestamp(int(since))
        except Exception as e:
            current_app.logger.error(f'Error formatting timestamp')
            abort(400)
        formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        query = f'ReceivedDateTime ge {formatted_timestamp}'
        try:
            resp = self.query_email_provider(query)
            current_app.logger.info(f'Email Query Response: {resp.json()}')
            count = resp.json().get('@odata.count', 0)
            return str(count > 0)
        except Exception as e:
            current_app.logger.error(f'Error searching email for user {session["email_addr"]}')
            abort(400)
    
