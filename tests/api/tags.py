import sys
import os
import common

from common import USER_ROOT

class TagTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        self.assertIsNone(self.get("tags/a", USER_ROOT).json())
        self.assertEqual(0, len(self.get("tags", USER_ROOT).json()))


    def test_root_create_tag(self):
        self.assertEqual(200, self.put("tags/a", USER_ROOT).status_code)
        self.assertEqual([ "a" ], self.get("tags/a", USER_ROOT).json()["path"])

        list = self.get("tags", USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual([ "a" ], list[0]["path"])


    def test_root_create_nested_tag(self):
        self.assertEqual(200, self.put("tags/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("tags/a/b", USER_ROOT).status_code)

        self.assertEqual([ "a", "b" ], self.get("tags/a/b", USER_ROOT).json()["path"])

        list = self.get("tags", USER_ROOT).json()
        self.assertEqual(2, len(list.children))
        self.assertEqual([ "a" ], list.children[0]["path"])


    def test_root_delete_tag(self):
        self.assertEqual(200, self.put("tags/a", USER_ROOT).status_code)
        self.assertEqual(200, self.delete("tags/a", USER_ROOT).status_code)
        self.assertIsNone(self.get("tags/a", USER_ROOT).json())
        self.assertEqual("b", self.get("users/b", USER_ROOT).json()["id"])
        self.assertEqual(0, len(self.get("tags", USER_ROOT).json()))


    def test_root_delete_nested_tag(self):
        self.assertEqual(200, self.put("tags/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("tags/a/b", USER_ROOT).status_code)
        self.assertEqual(200, self.put("tags/a/b/c", USER_ROOT).status_code)
        self.assertEqual(3, len(self.get("tags", USER_ROOT).json()))

        self.assertEqual(200, self.delete("tags/a/b", USER_ROOT).status_code)
        self.assertIsNone(self.get("tags/a", USER_ROOT).json())
        self.assertEqual(1, len(self.get("tags", USER_ROOT).json()))


if __name__ == "__main__":
    unittest.main()

    
