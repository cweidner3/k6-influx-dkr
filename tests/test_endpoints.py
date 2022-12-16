# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest

import requests

G_ORIGIN = 'http://localhost:8089'


class TestEndpoints(unittest.TestCase):

    def test_index(self):
        resp = requests.get(f'{G_ORIGIN}/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b'OK')

    def test_bad_args_run(self):
        resp = requests.get(f'{G_ORIGIN}/run')
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.content, b'Unauthorized')

    def test_good_run(self):
        resp = requests.get(f'{G_ORIGIN}/run', params={'secret': 'very-secret-phrase'})
        self.assertEqual(resp.status_code, 200)
