import sys
import os
import common

from common import USER_ROOT

class RemarkTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        self.assertEqual(0, len(self.get("test_harness/remarks/a", auth=USER_ROOT).json()))


    def test_root_create_remark(self):
        self.assertEqual(200, self.post("test_harness/remarks/a", auth=USER_ROOT).status_code)
        self.assertEqual(1, len(self.get("test_harness/remarks/a", auth=USER_ROOT).json()))


    def test_root_create_remarks(self):
        self.assertEqual(200, self.post("test_harness/remarks/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.post("test_harness/remarks/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.post("test_harness/remarks/a", auth=USER_ROOT).status_code)
        self.assertEqual(3, len(self.get("test_harness/remarks/a", auth=USER_ROOT).json()))


    def test_root_create_different_remarks(self):
        self.assertEqual(200, self.post("test_harness/remarks/a", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.post("test_harness/remarks/b", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.post("test_harness/remarks/b", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.post("test_harness/remarks/c", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.post("test_harness/remarks/c", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.post("test_harness/remarks/c", auth=USER_ROOT).status_code)
        self.assertEqual(1, len(self.get("test_harness/remarks/a", auth=USER_ROOT).json()))
        self.assertEqual(2, len(self.get("test_harness/remarks/b", auth=USER_ROOT).json()))
        self.assertEqual(3, len(self.get("test_harness/remarks/c", auth=USER_ROOT).json()))


if __name__ == "__main__":
    unittest.main()

    
