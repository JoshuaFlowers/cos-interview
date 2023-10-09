from GoogleAdapter import GoogleAdapter
from MicrosoftAdapter import MicrosoftAdapter
from authlib.integrations.flask_client import OAuth
from flask import Flask, request, abort, session, url_for
from flask_session import Session
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex()
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
oauth = OAuth(app)

app_url = 'https://hallowelt.uk'

SUCCESS_ROUTE = '/success'

GOOGLE_OAUTH_SUCCESS_ROUTE = '/google/oauth/success'
MICROSOFT_OAUTH_SUCCESS_ROUTE = '/microsoft/oauth/success'

adapters =  {
                'gmail.com': GoogleAdapter(oauth),
                'outlook.com': MicrosoftAdapter(oauth)
            }


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
    adapters['outlook.com'].oauth_success()
    return app.redirect(url_for('success'))

@app.route('/oauth/success')
def oauth_success():
    domain = session.get('domain')
    adapters[domain].oauth_success()
    return app.redirect(url_for('success'))

@app.route('/emails/search')
def search_emails():
    since = request.args.get('since')
    domain = session['domain']
    return adapters[domain].search_emails(since)

if __name__ == '__main__':
    app.run(debug=True)
