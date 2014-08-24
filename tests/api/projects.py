import sys
import os
import common
import time

from common import USER_ROOT

class ProjectTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        self.assertIsNone(self.get("projects/c/a", USER_ROOT).json())
        self.assertEqual(0, len(self.get("projects/c", USER_ROOT).json()))


    def test_root_create_project(self):
        self.assertEqual(200, self.put("projects/c/a", USER_ROOT).status_code)
        self.assertEqual("a", self.get("projects/c/a", USER_ROOT).json()["path"])
        self.assertEqual([ "a" ], self.get("projects/c/a", USER_ROOT).json()["key"])

        list = self.get("projects/c", USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["path"])
        self.assertEqual([ "a" ], list[0]["key"])


    def test_root_create_projects(self):
        self.assertEqual(200, self.put("projects/c/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("projects/c/b", USER_ROOT).status_code)
        self.assertEqual(200, self.put("projects/c/c", USER_ROOT).status_code)

        list = self.get("projects/c", USER_ROOT).json()
        self.assertEqual(3, len(list))
        self.assertEqual(set([ "a", "b", "c" ]), set([ list[0]["path"], list[1]["path"], list[2]["path"] ]))


    def test_root_create_nested_project(self):
        self.assertEqual(200, self.put("projects/c/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("projects/c/a/b", USER_ROOT).status_code)

        self.assertEqual("a/b", self.get("projects/c/a/b", USER_ROOT).json()["path"])

        list = self.get("projects/c", USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["path"])


    def test_root_delete_project(self):
        self.assertEqual(200, self.put("projects/c/a", USER_ROOT).status_code)
        self.assertEqual(200, self.delete("projects/c/a", USER_ROOT).status_code)
        time.sleep(0.5)
        self.assertEqual(0, len(self.get("projects/c", USER_ROOT).json()))
        self.assertEqual("a", self.get("projects/c/a", USER_ROOT).json()["path"])


    def test_root_delete_nested_project(self):
        self.assertEqual(200, self.put("projects/c/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("projects/c/a/b", USER_ROOT).status_code)
        self.assertEqual(200, self.put("projects/c/a/b/c", USER_ROOT).status_code)
        self.assertEqual(1, len(self.get("projects/c", USER_ROOT).json()))

        self.assertEqual(200, self.delete("projects/c/a/b", USER_ROOT).status_code)
        self.assertEqual(1, len(self.get("projects/c", USER_ROOT).json()))
        self.assertEqual(0, len(self.get("projects/c/a", USER_ROOT).json()["children"]))



if __name__ == "__main__":
    unittest.main()

    
