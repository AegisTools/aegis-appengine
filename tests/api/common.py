import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import lib.requests
import unittest

URL = "http://localhost:8080/"
HEADERS = { "Content-Type" : "application/json",
            "Accept"       : "application/json" }

USER_ROOT = lib.requests.Session()
USER_ANONYMOUS = lib.requests.Session()
USER_A = lib.requests.Session()
USER_B = lib.requests.Session()

USER_ROOT.get(URL + "_ah/login?email=root%40test.com&action=Login&admin=True")
USER_A.get(URL + "_ah/login?email=a%40test.com&action=Login&admin=")
USER_B.get(URL + "_ah/login?email=b%40test.com&action=Login&admin=")


class AegisTestCase(unittest.TestCase):

    def wipe(self):
        self.post("test_harness/wipe", auth=USER_ROOT)

    def setUp(self):
        self.wipe()

    def tearDown(self):
        # self.wipe()
        pass

    def get(self, fragment, auth=USER_ANONYMOUS):
        return auth.get(URL + fragment, headers=HEADERS)

    def put(self, fragment, payload=None, auth=USER_ANONYMOUS):
        return auth.put(URL + fragment, data=payload, headers=HEADERS)

    def post(self, fragment, payload=None, auth=USER_ANONYMOUS):
        return auth.post(URL + fragment, data=payload, headers=HEADERS)

    def delete(self, fragment, auth=USER_ANONYMOUS):
        return auth.delete(URL + fragment, headers=HEADERS)

