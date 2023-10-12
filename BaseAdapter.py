from flask import session, url_for, current_app
from authlib.integrations.flask_client import OAuth

class BaseAdapter:

    oauth = None

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
        try:
            self.oauth.register(name = self.name, **self.get_provider_data())
        except Exception as e:
            current_app.logger.error(f'Error registering {self.name} with oauth connector: \n {e}')

    def authorize(self, email_addr = None):
        redirect_uri = url_for('oauth_success', _external=True)
        auth_params = {'login_hint': email_addr}
        try:
            resp = getattr(self.oauth, self.name).authorize_redirect(redirect_uri, **auth_params)
            current_app.logger.info(f'Authorize: Status Code {resp.status_code}, Redirect URL: {resp.location}')
            return resp
        except Exception as e:
            current_app.logger.error(f'Error authorizing user {email_addr} with {self.name}:\n{e}')
            return None
    
    def success(self):
        return 'success'

    def exchange_for_token(self):
        return getattr(self.oauth, self.name).authorize_access_token()
    
    def oauth_success(self):
        try:
            token = self.exchange_for_token()
            email = session.get('email_addr')
            session['token'] = token
            current_app.logger.info(f'User authorization successful: {email}')
        except Exception as e:
            current_app.logger.error(f'Error exchanging auth code for token: {e}')
    
    def search_emails(self, since):
        raise NotImplementedError("This method should be implemented in the child class.")

    
