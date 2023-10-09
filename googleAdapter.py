from flask import session, url_for
from authlib.integrations.flask_client import OAuth

class GoogleAdapter:

    _CLIENT_ID = '698626242388-1cb2m9tkn0qmnhli127ei2v9ech1cndk.apps.googleusercontent.com'
    _CLIENT_SECRET = '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'
    _AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
    _ACCESS_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    _REFRESH_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    _SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    _OAUTH_SUCCESS_ROUTE = '/google/oauth/success'
    _TOKEN_EXCHANGE_SUCCESS_ROUTE = '/google/token/success'
    _MAIL_API_URL = 'https://www.googleapis.com/gmail/v1/users/me/messages'
    _SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


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
        self.name = "google"
        self.oauth = oauthConnector
        self.oauth.register(name = self.name, **self.get_provider_data())

    def authorize(self, email_addr = None):
        redirect_uri = url_for('google_oauth_success', _external=True)
        auth_params = {'login_hint': email_addr}
        return self.oauth.google.authorize_redirect(redirect_uri, **auth_params)
    
    def success(self):
        return 'success'
    
    def oauth_success(self):
        token = self.oauth.google.authorize_access_token()
        email = session.get('email_addr')
        session['token'] = token
        print(email)
    
    def search_emails(self, since):
        query = f'after:{since}'
        resp =  self.oauth.google.get(
                    self._MAIL_API_URL,
                    params = {  'q': query,
                                'maxResults': 1
                    }, 
                    token = session['token']
                )
        messages = resp.json().get('messages', [])
        return str(len(messages) > 0)

    
