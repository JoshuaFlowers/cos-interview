import unittest
import requests
from server import app, oauth
from dotenv import load_dotenv
from flask import url_for, session
import os
from urllib.parse import urlparse


connect_email_endpoint = 'http://localhost:8000/connect/email'


class TestServer(unittest.TestCase):

    def setUp(self):
        app.testing = True
        app.config['SERVER_NAME'] = 'localhost:8000'

        load_dotenv()

        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()
        self.client = None

    
    def test_connect_invalid_email(self):
        resp = self.client.get(connect_email_endpoint, query_string={'email': 'test@google.com'})
        self.assertEqual(resp.status_code, 400)
        resp = requests.get(connect_email_endpoint, params={'email': 123})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.get(connect_email_endpoint, query_string={'email': 'test@microsaft.com'})
        self.assertEqual(resp.status_code, 400)
    
    def test_connect_valid_email(self):
        test_google_email = 'test@gmail.com'
        resp = self.client.get(connect_email_endpoint, query_string = {'email': test_google_email})
        self.assertEqual(resp.status_code, 302)
        parsed_url = urlparse(resp.location)
        self.assertEqual(parsed_url.netloc, os.environ.get('GOOGLE_AUTH_URL'))
        self.assertEqual(parsed_url.path, os.environ.get('GOOGLE_AUTH_PATH'))
        with self.client.session_transaction() as session:
            self.assertEqual(session['email_addr'], test_google_email)
            self.assertNotEqual(session['domain'], 'outlook.com')
            self.assertEqual(session['domain'], 'gmail.com')

        test_microsoft_email = 'test@outlook.com'
        resp = self.client.get(connect_email_endpoint, query_string = {'email': test_microsoft_email})
        self.assertEqual(resp.status_code, 302)
        parsed_url = urlparse(resp.location)
        self.assertEqual(parsed_url.netloc, os.environ.get('MICROSOFT_AUTH_URL'))
        self.assertEqual(parsed_url.path, os.environ.get('MICROSOFT_AUTH_PATH'))
        with self.client.session_transaction() as session:
            self.assertNotEqual(session['email_addr'], test_google_email)
            self.assertEqual(session['email_addr'], test_microsoft_email)
            self.assertNotEqual(session['domain'], 'gmail.com')
            self.assertEqual(session['domain'], 'outlook.com')

