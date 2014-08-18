import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import requests
import unittest

USER_ROOT = ("root@unittests", "root")
URL = "http://localhost:8080/"
HEADERS = { "Content-Type" : "application/json",
            "Accept"       : "application/json" }

class AegisTestCase(unittest.TestCase):

    def wipe(self):
        self.post("test_harness/wipe", USER_ROOT)

    def setUp(self):
        self.wipe()

    def tearDown(self):
        # self.wipe()
        pass

    def get(self, fragment, auth=None):
        return requests.get(URL + fragment, auth=auth, headers=HEADERS)

    def put(self, fragment, payload=None, auth=None):
        return requests.put(URL + fragment, auth=auth, headers=HEADERS)

    def post(self, fragment, payload=None, auth=None):
        return requests.post(URL + fragment, auth=auth, headers=HEADERS)

    def delete(self, fragment, auth=None):
        return requests.delete(URL + fragment, auth=auth, headers=HEADERS)

