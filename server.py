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

SUCCESS_ROUTE = '/success'

GOOGLE_OAUTH_SUCCESS_ROUTE = '/google/oauth/success'
GOOGLE_TOKEN_EXCHANGE_SUCCESS_ROUTE = '/google/token/success'

MICROSOFT_OAUTH_SUCCESS_ROUTE = '/microsoft/oauth/success'
MICROSOFT_TOKEN_EXCHANGE_SUCCESS_ROUTE = '/microsoft/token/success'

adapters = {
            'gmail.com': googleAdapter(oauth)
        }


def microsoft_oauth(email_addr = None):
    redirect_uri = url_for('microsoft_oauth_success', _external=True)
    auth_params = {}
    return oauth.microsoft.authorize_redirect(redirect_uri, **auth_params)


@app.route('/connect/email')
def connect_email():
    email_addr = request.args.get('email')
    if email_addr is None:
        abort(400) #add better indicator

    email_addr_parts = email_addr.split('@')

    if len(email_addr_parts) != 2:
        abort(400)

    email_domain = email_addr_parts[1]

    if email_domain not in adapters:
        abort(400)

    session['email_addr'] = email_addr
    session['domain'] = email_domain

    return adapters[email_domain].authorize(email_addr = email_addr)


@app.route(SUCCESS_ROUTE)
def success():
    return "success"

@app.route(GOOGLE_OAUTH_SUCCESS_ROUTE)
def google_oauth_success():
    domain = 'gmail.com'
    adapters[domain].oauth_success()
    return app.redirect(url_for('success'))

@app.route(MICROSOFT_OAUTH_SUCCESS_ROUTE)
def microsoft_oauth_success():
    adapters['microsoft.com'].oauth_success()
    return app.redirect(url_for('success'))

@app.route('/emails/search')
def search_emails():
    since = request.args.get('since')
    domain = session['domain']
    return adapters[domain].search_emails(since)

if __name__ == '__main__':
    app.run(debug=True, ssl_context=('/etc/letsencrypt/live/hallowelt.uk/fullchain.pem', '/etc/letsencrypt/live/hallowelt.uk/privkey.pem'))
