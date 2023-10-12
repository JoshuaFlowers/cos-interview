from GoogleAdapter import GoogleAdapter
from MicrosoftAdapter import MicrosoftAdapter
from authlib.integrations.flask_client import OAuth
from flask import Flask, request, abort, session, url_for
from flask_session import Session
from logging.handlers import RotatingFileHandler
import logging
import os
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex()
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
oauth = OAuth(app)

if not os.path.exists('logs'):
    os.mkdir('logs')

# Setup a rotating file handler, max 10MB per file with a backup count of 10 files
file_handler = RotatingFileHandler('logs/cos_app.log', maxBytes=10*1024*1024, backupCount=10)
# Set the logging format
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)  # or DEBUG, ERROR, etc.
app.logger.addHandler(file_handler)

# Set the base logger level
app.logger.setLevel(logging.INFO)
app.logger.info('COS App startup')

app_url = 'https://hallowelt.uk'

SUCCESS_ROUTE = '/success'

adapters =  {
                'gmail.com': GoogleAdapter(oauth),
                'outlook.com': MicrosoftAdapter(oauth)
            }


@app.route('/connect/email')
def connect_email():
    email_addr = request.args.get('email')
    if email_addr is None:
        abort(400)

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

@app.route('/oauth/success')
def oauth_success():
    domain = session.get('domain')
    adapters[domain].oauth_success()
    return app.redirect(url_for('success'))

@app.route('/emails/search')
def search_emails():
    since = request.args.get('since')
    try:
        domain = session['domain']
    except KeyError as ke:
        app.logger.error(f'Error, domain not in session: {ke}')
        abort(400)
    except Exception as e:
        app.logger.error(f'Error getting domain from session: {e}')
        abort(400)
    return adapters[domain].search_emails(since)

if __name__ == '__main__':
    app.run(debug=False)
