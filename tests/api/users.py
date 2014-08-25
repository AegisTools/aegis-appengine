import sys
import os
import common

from common import USER_ROOT

class UserTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        self.assertIsNone(self.get("users/a", auth=USER_ROOT).json())
        self.assertEqual(0, len(self.get("users", auth=USER_ROOT).json()))


    def test_root_create_user(self):
        self.assertEqual(200, self.put("users/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])

        list = self.get("users", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["key"])


    def test_root_delete_user(self):
        self.assertEqual(200, self.put("users/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])
        self.assertEqual(200, self.delete("users/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])
        self.assertEqual(0, len(self.get("users", auth=USER_ROOT).json()))


    def test_root_create_2_users(self):
        self.assertEqual(200, self.put("users/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/b", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])
        self.assertEqual("b", self.get("users/b", auth=USER_ROOT).json()["key"])

        list = self.get("users", auth=USER_ROOT).json()
        self.assertEqual(2, len(list))
        self.assertEqual(set(["a", "b"]), set([ list[0]["key"], list[1]["key"] ]))


    def test_root_delete_1_of_2_users(self):
        self.assertEqual(200, self.put("users/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("users/b", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])
        self.assertEqual("b", self.get("users/b", auth=USER_ROOT).json()["key"])

        self.assertEqual(200, self.delete("users/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("users/a", auth=USER_ROOT).json()["key"])
        self.assertEqual("b", self.get("users/b", auth=USER_ROOT).json()["key"])

        list = self.get("users", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("b", list[0]["key"])


if __name__ == "__main__":
    unittest.main()

    
