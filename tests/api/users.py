import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import requests
import unittest

USER_ROOT = ("root@unittests", "root")
URL = "http://localhost:8080/"

class TestUsers(unittest.TestCase):
    def wipe(self):
        self.post("wipe", USER_ROOT)

    def setUp(self):
        self.wipe()


    def test_root_create_user(self):
        self.assertIsNone(self.get("users/a", USER_ROOT).json())
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", USER_ROOT).json()["id"])


    def get(self, fragment, auth=None):
        return requests.get(URL + fragment + "?format=json", auth=auth)

    def put(self, fragment, payload=None, auth=None):
        return requests.put(URL + fragment + "?format=json", auth=auth)

    def post(self, fragment, payload=None, auth=None):
        return requests.post(URL + fragment + "?format=json", auth=auth)

if __name__ == "__main__":
    unittest.main()

    
