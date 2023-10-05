from flask import Flask, request, abort
import google.oauth2.credentials
import google_auth_oauthlib.flow

app = Flask(__name__)

#app_url = 'https://hallowelt.uk'
app_url = "https://localhost:5000"


def microsoft_oauth(email_addr = None):
    return 200

def google_oauth(email_addr = None):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'gmail_client_secret.json',
    scopes=['https://www.googleapis.com/auth/gmail.readonly'])
    flow.redirect_uri = app_url + '/success'
    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    print(authorization_url)
    return app.redirect(authorization_url)

@app.route('/connect/email')
def connect_email():
    #get email address from query parameters
    email_addr = request.args.get('email')
    if email_addr is None:
        abort(400) #add better indicator
    email_addr_parts = email_addr.split('@')
    for part in email_addr_parts:
        print(part)
    if len(email_addr_parts) != 2:
        abort(400)
    email_domain = email_addr_parts[1]
    #for handling generic email addresses a TLD package would be used to determine valid tlds
    #assume for simplicity that address will either be @microsoft.com or @gmail.com
    valid_domains = ['microsoft.com', 'gmail.com']
    if email_domain not in valid_domains:
        abort(400)
    if email_domain == 'microsoft.com':
        microsoft_oauth(email_addr = email_addr)
    elif email_domain == 'gmail.com':
        return google_oauth(email_addr = email_addr)
    else:
        abort(400)
    print(email_addr)
    return email_addr

#success_page = app_url + '/success'
success_page = 'http://localhost:5000/success'

@app.route('/success')
def success():
    return "success"
@app.route('/google/success')
def google_success():
    auth_code = request.args.get('code')
    print(auth_code)
    return app.redirect(success_page)
    



if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
