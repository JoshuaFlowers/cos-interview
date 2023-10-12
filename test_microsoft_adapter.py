from MicrosoftAdapter import MicrosoftAdapter
from dotenv import load_dotenv
from flask import Flask, url_for, session
from server import app, oauth
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs
import os
import unittest
from MockResponse import MockResponse

mock_token_json = { 'access_token': 'mock_microsoft_access_token',
                    'expires_in': 3599, 'scope': 'mock_microsoft_scope',
                    'token_type': 'Bearer', 'expires_at': 1697080026 }



class TestMicrosoftAdapter(unittest.TestCase):
    
    
    def setUp(self):
        app.testing = True
        app.config['SERVER_NAME'] = 'localhost:8000'
        
        load_dotenv()
        
        self.microsoft_adapter = MicrosoftAdapter(oauth)
        
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()


    def test_get_provider_data(self):
        provider_data = self.microsoft_adapter.get_provider_data()
        self.assertIsInstance(provider_data, dict)
        self.assertIn('client_id', provider_data)
        self.assertEqual(provider_data['client_id'], os.environ.get('MICROSOFT_CLIENT_ID'))
        self.assertEqual(provider_data['client_secret'], os.environ.get('MICROSOFT_CLIENT_SECRET'))
    
    
    def test_microsoft_authorize(self):
        resp = self.client.get('/connect/email?email=test@outlook.com')
        self.assertEqual(resp.status_code, 302)
        redirect_location = resp.location
        parsed_url = urlparse(redirect_location)
        query_params = parse_qs(parsed_url.query)
        self.assertEqual(query_params['client_id'][0], os.environ.get('MICROSOFT_CLIENT_ID'))
        self.assertEqual(parsed_url.netloc, os.environ.get('MICROSOFT_AUTH_URL'))
        self.assertEqual(parsed_url.path, os.environ.get('MICROSOFT_AUTH_PATH'))
        with self.client.session_transaction() as session:
            self.assertIn('domain', session)
            self.assertEqual(session['domain'], 'outlook.com')

    def test_microsoft_oauth_success(self):

        with patch.object( MicrosoftAdapter, 'exchange_for_token',
                return_value = mock_token_json ) as mock_exhange_for_token:
            with self.client.session_transaction() as session:
                session['email_addr'] = 'test@outlook.com'
                session['domain'] = 'outlook.com'

            resp = self.client.get(url_for('oauth_success'))

            with self.client.session_transaction() as session:
                self.assertEqual(session['token'], mock_token_json)

    def test_microsoft_email_search(self):
        with patch.object( MicrosoftAdapter, "query_email_provider",
                return_value = MockResponse({'@odata.count': 4}, 200) ):
            email_search = self.microsoft_adapter.search_emails(12345)
            self.assertEqual(email_search, 'True')

        with patch.object( MicrosoftAdapter, "query_email_provider",
                return_value = MockResponse({'@odata.count': 0}, 200) ):
            email_search = self.microsoft_adapter.search_emails(12345)
            self.assertEqual(email_search, 'False')
