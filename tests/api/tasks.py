import sys
import os
import common
import time

from common import USER_ROOT

class TaskTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        self.assertIsNone(self.get("tasks/a", auth=USER_ROOT).json())
        self.assertEqual(0, len(self.get("tasks", auth=USER_ROOT).json()))


    def test_root_create_task(self):
        self.assertEqual(200, self.put("tasks/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("tasks/a", auth=USER_ROOT).json()["path"])
        self.assertEqual([ "a" ], self.get("tasks/a", auth=USER_ROOT).json()["key"])

        list = self.get("tasks", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["path"])
        self.assertEqual([ "a" ], list[0]["key"])


    def test_root_create_tasks(self):
        self.assertEqual(200, self.put("tasks/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("tasks/b", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("tasks/c", auth=USER_ROOT).status_code)

        list = self.get("tasks", auth=USER_ROOT).json()
        self.assertEqual(3, len(list))
        self.assertEqual(set([ "a", "b", "c" ]), set([ list[0]["path"], list[1]["path"], list[2]["path"] ]))


    def test_root_create_nested_task(self):
        self.assertEqual(200, self.put("tasks/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("tasks/a/b", auth=USER_ROOT).status_code)

        self.assertEqual("a/b", self.get("tasks/a/b", auth=USER_ROOT).json()["path"])

        list = self.get("tasks", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["path"])


    def test_root_delete_task(self):
        self.assertEqual(200, self.put("tasks/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.delete("tasks/a", auth=USER_ROOT).status_code)
        time.sleep(0.5)
        self.assertEqual(0, len(self.get("tasks", auth=USER_ROOT).json()))
        self.assertEqual("a", self.get("tasks/a", auth=USER_ROOT).json()["path"])
        self.assertEqual([ "a" ], self.get("tasks/a", auth=USER_ROOT).json()["key"])


    def test_root_delete_nested_task(self):
        self.assertEqual(200, self.put("tasks/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("tasks/a/b", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("tasks/a/b/c", auth=USER_ROOT).status_code)
        self.assertEqual(1, len(self.get("tasks", auth=USER_ROOT).json()))

        self.assertEqual(200, self.delete("tasks/a/b", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("tasks/a", auth=USER_ROOT).json()["path"])
        self.assertEqual("a/b", self.get("tasks/a/b", auth=USER_ROOT).json()["path"])
        self.assertEqual("a/b/c", self.get("tasks/a/b/c", auth=USER_ROOT).json()["path"])
        self.assertEqual(1, len(self.get("tasks", auth=USER_ROOT).json()))



if __name__ == "__main__":
    unittest.main()

    
