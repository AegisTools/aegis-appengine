import sys
import os
import common

from common import USER_ROOT

class UserTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        self.assertIsNone(self.get("users/a", USER_ROOT).json())
        self.assertEqual(0, len(self.get("users", USER_ROOT).json()))


    def test_root_create_user(self):
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", USER_ROOT).json()["id"])

        list = self.get("users", USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["user"])


    def test_root_delete_user(self):
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", USER_ROOT).json()["id"])
        self.assertEqual(200, self.delete("users/a", USER_ROOT).status_code)
        self.assertIsNone(self.get("users/a", USER_ROOT).json())
        self.assertEqual(0, len(self.get("users", USER_ROOT).json()))


    def test_root_create_2_users(self):
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/b", USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", USER_ROOT).json()["id"])
        self.assertEqual("b", self.get("users/b", USER_ROOT).json()["id"])

        list = self.get("users", USER_ROOT).json()
        self.assertEqual(2, len(list))
        self.assertEqual(set(["a", "b"]), set([ list[0]["user"], list[1]["user"] ]))


    def test_root_delete_1_of_2_users(self):
        self.assertEqual(200, self.put("users/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/b", USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", USER_ROOT).json()["id"])
        self.assertEqual("b", self.get("users/b", USER_ROOT).json()["id"])

        self.assertEqual(200, self.delete("users/a", USER_ROOT).status_code)
        self.assertIsNone(self.get("users/a", USER_ROOT).json())
        self.assertEqual("b", self.get("users/b", USER_ROOT).json()["id"])


if __name__ == "__main__":
    unittest.main()

    
