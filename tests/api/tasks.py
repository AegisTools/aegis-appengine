import sys
import os
import common

from common import USER_ROOT

class TaskTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        self.assertIsNone(self.get("tasks/a", USER_ROOT).json())
        self.assertEqual(0, len(self.get("tasks", USER_ROOT).json()))


    def test_root_create_task(self):
        self.assertEqual(200, self.put("tasks/a", USER_ROOT).status_code)
        self.assertEqual("a", self.get("tasks/a", USER_ROOT).json()["path"])
        self.assertEqual([ "a" ], self.get("tasks/a", USER_ROOT).json()["key"])

        list = self.get("tasks", USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["path"])
        self.assertEqual([ "a" ], list[0]["key"])


    def test_root_create_tasks(self):
        self.assertEqual(200, self.put("tasks/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("tasks/b", USER_ROOT).status_code)
        self.assertEqual(200, self.put("tasks/c", USER_ROOT).status_code)

        list = self.get("tasks", USER_ROOT).json()
        self.assertEqual(3, len(list))
        self.assertEqual(set([ "a", "b", "c" ]), set([ list[0]["path"], list[1]["path"], list[2]["path"] ]))


    def test_root_create_nested_task(self):
        self.assertEqual(200, self.put("tasks/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("tasks/a/b", USER_ROOT).status_code)

        self.assertEqual("a/b", self.get("tasks/a/b", USER_ROOT).json()["path"])

        list = self.get("tasks", USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["path"])


    def test_root_delete_task(self):
        self.assertEqual(200, self.put("tasks/a", USER_ROOT).status_code)
        self.assertEqual(200, self.delete("tasks/a", USER_ROOT).status_code)
        self.assertIsNone(self.get("tasks/a", USER_ROOT).json())


    def test_root_delete_nested_task(self):
        self.assertEqual(200, self.put("tasks/a", USER_ROOT).status_code)
        self.assertEqual(200, self.put("tasks/a/b", USER_ROOT).status_code)
        self.assertEqual(200, self.put("tasks/a/b/c", USER_ROOT).status_code)
        self.assertEqual(1, len(self.get("tasks", USER_ROOT).json()))

        self.assertEqual(200, self.delete("tasks/a/b", USER_ROOT).status_code)
        self.assertIsNone(self.get("tasks/a/b", USER_ROOT).json())
        self.assertIsNone(self.get("tasks/a/b/c", USER_ROOT).json())
        self.assertEqual(1, len(self.get("tasks", USER_ROOT).json()))



if __name__ == "__main__":
    unittest.main()

    
