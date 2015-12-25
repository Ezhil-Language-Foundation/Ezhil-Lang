# -*- coding: utf-8 -*-

import json
from django.test import TestCase, Client

# Create your tests here.


class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_valid_ezhil_code(self):
        code = u'பதிப்பி "வணக்கம்!"'
        response = self.client.post('/api/', content_type='application/json',
                                    data=json.dumps({'code': code}))
        expected_response = {'result': u"வணக்கம்!\n", 'is_success': True}

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_response)

    def test_invalid_ezhil_code(self):
        code = u'print("welcome")'
        response = self.client.post('/api/', content_type='application/json',
                                    data=json.dumps({'code': code}))
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['is_success'], False)

    def test_with_missing_post_param(self):
        response = self.client.post('/api/')

        self.assertEqual(response.status_code, 400)
        expected_response = {"error": "Non json data found"}
        self.assertEqual(json.loads(response.content), expected_response)
