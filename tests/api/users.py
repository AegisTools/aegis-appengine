import sys
import os
import common
import time

from common import USER_ROOT

class UserTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        time.sleep(1)
        self.assertEqual(3, len(self.get("users", auth=USER_ROOT).json()))
        self.assertEqual(404, self.get("users/a", auth=USER_ROOT).status_code)


    def test_root_create_user(self):
        self.assertEqual(200, self.put("users/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])

        list = self.get("users", auth=USER_ROOT).json()
        self.assertEqual(4, len(list))
        self.assertEqual(set(["a", "a@test.com", "b@test.com", "root@test.com"]), set([ item["key"] for item in list ]))


    def test_root_delete_user(self):
        self.assertEqual(200, self.put("users/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])
        self.assertEqual(200, self.delete("users/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])
        self.assertEqual(3, len(self.get("users", auth=USER_ROOT).json()))


    def test_root_create_2_users(self):
        self.assertEqual(200, self.put("users/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/b", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])
        self.assertEqual("b", self.get("users/b", auth=USER_ROOT).json()["key"])

        list = self.get("users", auth=USER_ROOT).json()
        self.assertEqual(5, len(list))
        self.assertEqual(set(["a", "b", "a@test.com", "b@test.com", "root@test.com"]), set([ item["key"] for item in list ]))


    def test_root_delete_1_of_2_users(self):
        self.assertEqual(200, self.put("users/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/b", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])
        self.assertEqual("b", self.get("users/b", auth=USER_ROOT).json()["key"])

        self.assertEqual(200, self.delete("users/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])
        self.assertEqual("b", self.get("users/b", auth=USER_ROOT).json()["key"])

        list = self.get("users", auth=USER_ROOT).json()
        self.assertEqual(4, len(list))
        self.assertEqual(set(["b", "a@test.com", "b@test.com", "root@test.com"]), set([ item["key"] for item in list ]))


if __name__ == "__main__":
    unittest.main()

    
