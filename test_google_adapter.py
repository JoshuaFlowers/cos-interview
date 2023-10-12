from GoogleAdapter import GoogleAdapter
from dotenv import load_dotenv
from flask import Flask, session, url_for
from server import app, oauth
from unittest.mock import patch
from urllib.parse import urlparse, parse_qs
import os
import unittest
from MockResponse import MockResponse


mock_token_json = { 'access_token': 'mock_google_access_token',
                    'expires_in': 3599, 'scope': 'mock_google_scope',
                    'token_type': 'Bearer', 'expires_at': 1697080026 }


class TestGoogleAdapter(unittest.TestCase):
    
    
    def setUp(self):
        app.testing = True
        app.config['SERVER_NAME'] = 'localhost:8000'
        
        load_dotenv()
        
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()
        self.google_adapter = GoogleAdapter(oauth)

    def tearDown(self):
        self.ctx.pop()
        self.google_adapter = None


    def test_get_provider_data(self):
        provider_data = self.google_adapter.get_provider_data()
        self.assertIsInstance(provider_data, dict)
        self.assertIn('client_id', provider_data)
        self.assertEqual(provider_data['client_id'], os.environ.get('GOOGLE_CLIENT_ID'))
        self.assertEqual(provider_data['client_secret'], os.environ.get('GOOGLE_CLIENT_SECRET'))
    
    
    def test_google_authorize(self):
        resp = self.client.get('/connect/email?email=test@gmail.com')
        self.assertEqual(resp.status_code, 302)
        redirect_location = resp.location
        parsed_url = urlparse(redirect_location)
        query_params = parse_qs(parsed_url.query)
        self.assertEqual(query_params['client_id'][0], os.environ.get('GOOGLE_CLIENT_ID'))
        self.assertEqual(parsed_url.netloc, 'accounts.google.com')
        self.assertEqual(parsed_url.path, '/o/oauth2/auth')
        with self.client.session_transaction() as session:
            self.assertIn('domain', session)
            self.assertEqual(session['domain'], 'gmail.com')


    def test_google_oauth_success(self):

        with patch.object( GoogleAdapter, 'exchange_for_token',
                return_value = mock_token_json ) as mock_exchange_for_token:

            with self.client.session_transaction() as session:
                session['email_addr'] = 'test@gmail.com'
                session['domain'] = 'gmail.com'

            resp = self.client.get(url_for('oauth_success'))

            with self.client.session_transaction() as session:
                self.assertEqual(session['token'], mock_token_json)

    def test_google_email_search(self):
        with patch.object( GoogleAdapter, 'query_email_provider',
                return_value = MockResponse({'messages': [{'id': 'testingId'}]}, 200 ) ):
            email_search = self.google_adapter.search_emails(12345)
            self.assertEqual(email_search, 'True')

        with patch.object( GoogleAdapter, 'query_email_provider',
                return_value = MockResponse({'messages': []}, 200 ) ):
            email_search = self.google_adapter.search_emails(12345)
            self.assertEqual(email_search, 'False')


        assert True
