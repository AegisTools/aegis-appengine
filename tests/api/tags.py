import sys
import os
import common

from common import USER_ROOT

class TagTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        self.assertIsNone(self.get("tags/a", auth=USER_ROOT).json())
        self.assertEqual(0, len(self.get("tags", auth=USER_ROOT).json()))


    def test_root_create_tag(self):
        self.assertEqual(200, self.put("tags/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("tags/a", auth=USER_ROOT).json()["path"])
        self.assertEqual([ "a" ], self.get("tags/a", auth=USER_ROOT).json()["key"])

        list = self.get("tags", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["path"])
        self.assertEqual([ "a" ], list[0]["key"])


    def test_root_create_tags(self):
        self.assertEqual(200, self.put("tags/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("tags/b", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("tags/c", auth=USER_ROOT).status_code)

        list = self.get("tags", auth=USER_ROOT).json()
        self.assertEqual(3, len(list))
        self.assertEqual(set([ "a", "b", "c" ]), set([ list[0]["path"], list[1]["path"], list[2]["path"] ]))


    def test_root_create_nested_tag(self):
        self.assertEqual(200, self.put("tags/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("tags/a/b", auth=USER_ROOT).status_code)

        self.assertEqual("a/b", self.get("tags/a/b", auth=USER_ROOT).json()["path"])

        list = self.get("tags", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0]["path"])


    def test_root_delete_tag(self):
        self.assertEqual(200, self.put("tags/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.delete("tags/a", auth=USER_ROOT).status_code)
        self.assertEqual("a", self.get("tags/a", auth=USER_ROOT).json()["path"])
        self.assertEqual(0, len(self.get("tags", auth=USER_ROOT).json()))


    def test_root_delete_nested_tag(self):
        self.assertEqual(200, self.put("tags/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("tags/a/b", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("tags/a/b/c", auth=USER_ROOT).status_code)
        self.assertEqual(1, len(self.get("tags", auth=USER_ROOT).json()))

        self.assertEqual(200, self.delete("tags/a/b", auth=USER_ROOT).status_code)
        self.assertEqual("a/b", self.get("tags/a/b", auth=USER_ROOT).json()["path"])
        self.assertEqual("a/b/c", self.get("tags/a/b/c", auth=USER_ROOT).json()["path"])
        self.assertEqual(1, len(self.get("tags", auth=USER_ROOT).json()))
        self.assertEqual(0, len(self.get("tags/a", auth=USER_ROOT).json()["children"]))


    def test_root_apply_tag(self):
        self.assertEqual(200, self.put("test_harness/tag/thing/a", auth=USER_ROOT).status_code)

        list = self.get("test_harness/tag/thing", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0])


    def test_root_reapply_tag(self):
        self.assertEqual(200, self.put("test_harness/tag/thing/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/tag/thing/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/tag/thing/a", auth=USER_ROOT).status_code)
        
        list = self.get("test_harness/tag/thing", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0])



    def test_root_apply_multiple_tags(self):
        self.assertEqual(200, self.put("test_harness/tag/thing/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/tag/thing/b", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/tag/thing/c/d", auth=USER_ROOT).status_code)
        
        list = self.get("test_harness/tag/thing", auth=USER_ROOT).json()
        self.assertEqual(3, len(list))
        self.assertEqual(set([ "a", "b", "c/d"]), set(list))


    def test_root_remove_tag(self):
        self.assertEqual(200, self.put("test_harness/tag/thing/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/tag/thing/b", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.delete("test_harness/tag/thing/b", auth=USER_ROOT).status_code)
        
        list = self.get("test_harness/tag/thing", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a", list[0])

    def test_root_remove_parent_tag(self):
        self.assertEqual(200, self.put("test_harness/tag/thing/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/tag/thing/a/b", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.delete("test_harness/tag/thing/a", auth=USER_ROOT).status_code)

        list = self.get("test_harness/tag/thing", auth=USER_ROOT).json()
        self.assertEqual(1, len(list))
        self.assertEqual("a/b", list[0])



if __name__ == "__main__":
    unittest.main()

    
