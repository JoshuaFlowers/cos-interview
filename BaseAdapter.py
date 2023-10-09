from flask import session, url_for
from authlib.integrations.flask_client import OAuth

class BaseAdapter:

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
        self.oauth = oauthConnector
        self.oauth.register(name = self.name, **self.get_provider_data())

    def authorize(self, email_addr = None):
        redirect_uri = url_for('oauth_success', _external=True)
        auth_params = {'login_hint': email_addr}
        return getattr(self.oauth, self.name).authorize_redirect(redirect_uri, **auth_params)
    
    def success(self):
        return 'success'
    
    def oauth_success(self):
        token = getattr(self.oauth, self.name).authorize_access_token()
        email = session.get('email_addr')
        session['token'] = token
        print(email)#change to log
    
    def search_emails(self, since):
        raise NotImplementedError("This method should be implemented in the child class.")

    
