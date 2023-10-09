from cosDB import cosDB
from datetime import datetime
from flask import session, url_for
from authlib.integrations.flask_client import OAuth

class MicrosoftAdapter:

    _CLIENT_ID = 'cf508a2c-075d-4fdf-ad64-2f52da1137a0'
    _CLIENT_SECRET = '71.8Q~3MnLeTlg0YRZT7N1hp5ONL~7H7UFB9RdrH'
    _AUTH_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize'
    _ACCESS_TOKEN_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token'
    _REFRESH_TOKEN_URL = 'https://login.microsoftonline.com/consumers/oauth2/v2.0/token'
    _SCOPES = ['Mail.Read']
    _OAUTH_SUCCESS_ROUTE = '/microsoft/oauth/success'
    _TOKEN_EXCHANGE_SUCCESS_ROUTE = '/microsoft/token/success'
    _MAIL_API_URL = 'https://graph.microsoft.com/v1.0/me/messages'


    def get_provider_data(self):
        return {
                    'client_id': self._CLIENT_ID,
                    'client_secret': self._CLIENT_SECRET,
                    'authorize_url': self._AUTH_URL,
                    'authorize_params': {'access_type': 'offline'},
                    'access_token_url': self._ACCESS_TOKEN_URL,
                    'access_token_params': None,
                    'refresh_token_url': self._REFRESH_TOKEN_URL,
                    'redirect_to': self._OAUTH_SUCCESS_ROUTE,
                    'client_kwargs': {'scope': ' '.join(self._SCOPES)}
                }

    def __init__(self, oauthConnector):
        self.name = "microsoft"
        self.oauth = oauthConnector
        self.oauth.register(name = self.name, **self.get_provider_data())


    def authorize(self, email_addr = None):
        redirect_uri = url_for('microsoft_oauth_success', _external=True)
        auth_params = {'login_hint': email_addr}
        return self.oauth.microsoft.authorize_redirect(redirect_uri, **auth_params)
    
    def success(self):
        return 'success'
    
    def oauth_success(self):
        token = self.oauth.microsoft.authorize_access_token()
        email = session.get('email_addr')
        session['token'] = token
        print(email)
    
    def search_emails(self, since):
        timestamp = datetime.utcfromtimestamp(int(since))
        formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        query = f'ReceivedDateTime ge {formatted_timestamp}'
        resp =  self.oauth.microsoft.get(
                    self._MAIL_API_URL,
                    params = {  '$filter': query,
                                '$count': 'true',
                                '$select': 'receivedDateTime', 
                                '$top': 1 
                    },
                    token = session['token']
                )
        messages = resp.json().get('messages', [])
        count = resp.json().get('@odata.count', 0)
        return str(count > 0)
    
