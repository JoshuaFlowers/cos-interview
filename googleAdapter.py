from cosDB import cosDB
from flask import Flask, request, abort, session, url_for
from flask_session import Session
from authlib.integrations.flask_client import OAuth
import json

class googleAdapter:

#project_id='chiefofstaff-interview-test'
#auth_provider_x509_cert_url='https://www.googleapis.com/oauth2/v1/certs'

    _CLIENT_ID = '698626242388-1cb2m9tkn0qmnhli127ei2v9ech1cndk.apps.googleusercontent.com'
    _CLIENT_SECRET = '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'
    _AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
    _ACCESS_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    _REFRESH_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    _CLIENT_SECRETS_LOCATION = 'gmail_client_secret.json'
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

    def __init__(self, oauthConnector):#, session):
        self.name = "google"
        self.oauth = oauthConnector
        #self.session = session
        self.oauth.register(name = self.name, **self.get_provider_data())

    def authorize(self, email_addr = None):
        redirect_uri = url_for('google_oauth_success', _external=True)
        auth_params = {'login_hint': email_addr}
        return self.oauth.google.authorize_redirect(redirect_uri, **auth_params)
    
    SUCCESS_ROUTE = '/success'
    #success_page = app_url + SUCCESS_ROUTE
    
    def success(self):
        #self.session.clear()
        return 'success'
    
    def google_oauth_success(self):
        token = self.oauth.google.authorize_access_token()
        email = session.get('email_addr')
        print(email)
        if token is not None:
            insert_user(email, 1, json.dumps(token))
        print(token)
        return app.redirect(url_for(success, _external=True))
    
    def search_emails(self, since):
        #since = request.args.get('since')
        #query_string = f'maxResults=1&q=after:{since}'
        query = f'after:{since}'
        resp = self.oauth.get(self._MAIL_API_URL, params={'q': query, 'maxResults': 1})

    
