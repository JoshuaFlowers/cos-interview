from cosDB import cosDB
import requests
from flask import Flask, request, abort, session, url_for
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from googleapiclient.discovery import build
import secrets
import json
import time
from googleAdapter import googleAdapter

app = Flask(__name__)

app.secret_key = secrets.token_hex()
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
oauth = OAuth(app)

app_url = 'https://hallowelt.uk'

GOOGLE_CLIENT_SECRETS_LOCATION = 'gmail_client_secret.json'
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GOOGLE_OAUTH_SUCCESS_ROUTE = '/google/oauth/success'
GOOGLE_TOKEN_EXCHANGE_SUCCESS_ROUTE = '/google/token/success'


MICROSOFT_OAUTH_SUCCESS_ROUTE = '/microsoft/oauth/success'

adapters = {
        'gmail.com': googleAdapter(oauth)#, session)
        }

google_client_json = None
with open(GOOGLE_CLIENT_SECRETS_LOCATION, 'rb') as f:
    google_client_json = json.loads(f.read())
if 'web' in google_client_json:
    google_client_json = google_client_json['web']

OAUTH_PROVIDERS = {
    'google': {
        'client_id':google_client_json['client_id'],
        'client_secret':google_client_json['client_secret'],
        'authorize_url':google_client_json['auth_uri'],
        'authorize_params':{'access_type': 'offline'},
        'access_token_url':google_client_json['token_uri'],
        'access_token_params':None,
        'refresh_token_url':google_client_json['token_uri'],
        'redirect_to':GOOGLE_OAUTH_SUCCESS_ROUTE,
        'client_kwargs':{'scope': ' '.join(GOOGLE_SCOPES), 'code_challenge_method': 'S256'}
    },
}

for provider_name, provider_data in OAUTH_PROVIDERS.items():
    oauth.register(name=provider_name, **provider_data)



def microsoft_oauth(email_addr = None):
    redirect_uri = url_for('microsoft_oauth_success', _external=True)
    auth_params = {}
    return oauth.microsoft.authorize_redirect(redirect_uri, **auth_params)

def google_oauth(email_addr = None):
    redirect_uri = url_for('google_oauth_success', _external=True)
    auth_params = {'login_hint': email_addr}
    return oauth.google.authorize_redirect(redirect_uri, **auth_params)

def insert_user(email, authorized, token, last_authenticated):
    #***add code to handle case where user already exists***
    db = cosDB()
    db.insert_user(email, authorized, token, last_authenticated)

def refresh_user_token(email, token):
    if 'refresh_token' not in token:
        return None
    refresh_token = token['refresh_token']
    return None

def get_user_token(email):
    db = cosDB()
    user = db.get_user(email)
    if user is None:
        return None
    token = user['token']
    if token is None or len(token) < 1:
        return None
    token = json.loads(token)
    curr_time = int(time.time())
    if 'expires_at' in token:
        expires_at = token['expires_at']
        if expires_at < curr_time:
            return refresh_user_token(user, token)
    return token

@app.route('/connect/email')
def connect_email():
    email_addr = request.args.get('email')
    if email_addr is None:
        abort(400) #add better indicator

    email_addr_parts = email_addr.split('@')
    if len(email_addr_parts) != 2:
        abort(400)

    email_domain = email_addr_parts[1]
    valid_domains = ['microsoft.com', 'gmail.com']
    auth_funcs = {
        'microsoft.com': microsoft_oauth,
        'gmail.com': google_oauth
    }
    #if email_domain not in valid_domains:
    if email_domain not in auth_funcs:
        abort(400)

    session['email_addr'] = email_addr

    print(auth_funcs[email_domain])
    #return auth_funcs[email_domain](email_addr = email_addr)
    return adapters[email_domain].authorize(email_addr = email_addr)

SUCCESS_ROUTE = '/success'
success_page = app_url + SUCCESS_ROUTE

@app.route(SUCCESS_ROUTE)
def success():
    #session.clear()
    return "success"

@app.route(GOOGLE_OAUTH_SUCCESS_ROUTE)
def google_oauth_success():
    token = oauth.google.authorize_access_token()
    email = session.get('email_addr')
    print(email)
    if token is not None:
        insert_user(email, 1, json.dumps(token), int(time.time()))
    print(token)
    return app.redirect(success_page)

@app.route(MICROSOFT_OAUTH_SUCCESS_ROUTE)
def microsoft_oauth_success():
    token = oauth.microsoft.authorize_access_token()
    email = session.get('email_addr')
    print(email)
    if token is not None:
        insert_user(email, 1, json.dumps(token), int(time.time()))
    print(token)
    return app.redirect(success_page)

def search_google_emails():
    url = "https://www.googleapis.com/gmail/v1/users/me/messages"

    # Your access token from the OAuth process
    access_token = "YOUR_ACCESS_TOKEN"
    
    # Headers for authentication
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Parameters for the search query
    params = {
        "q": "after:2023-10-05"  # Adjust the date as needed
    }
    
    # Make the GET request
    response = requests.get(url, headers=headers, params=params)
    
    # Parse the JSON response
    messages = response.json().get('messages', [])

@app.route('/emails/search')
def search_emails():
    since = request.args.get('since')
    user = request.args.get('user')
    url = "https://www.googleapis.com/gmail/v1/users/%s/messages" % user
    query = 'maxResults=1&q=after:%s' % since
    token = json.loads(get_user_token(user))
    access_token = token['access_token']
    #user = session['email_addr']
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "q": "after:%s" % since,
        'maxResults': 1
    }
    response = requests.get(url, headers=headers, params=params)
    messages = response.json().get('messages', [])
    print(response.json())
    print(messages)
    return ""
    try:
        response = service.users().messages().list(userId=user, q=query).execute()
        print(response)
        messages = response['messages']
        return len(messages) > 0
    except Exception as e:
        print(e)
    return None


if __name__ == '__main__':
    app.run(debug=True, ssl_context=('/etc/letsencrypt/live/hallowelt.uk/fullchain.pem', '/etc/letsencrypt/live/hallowelt.uk/privkey.pem'))
