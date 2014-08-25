import sys
import os
import common

from common import USER_ROOT

class PermissionTests(common.AegisTestCase):

    def test_wipe_cleared_data(self):
        self.assertFalse(self.get("test_harness/permissions/user/action/kind", auth=USER_ROOT).json()["allowed"])


    def test_root_grant_permission_no_key(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind", auth=USER_ROOT).status_code)
        self.assertTrue(self.get("test_harness/permissions/user/action/kind", auth=USER_ROOT).json()["allowed"])
        self.assertFalse(self.get("test_harness/permissions/user/other_action/kind", auth=USER_ROOT).json()["allowed"])


    def test_root_grant_permission_with_key(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind/a", auth=USER_ROOT).status_code)
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a", auth=USER_ROOT).json()["allowed"])
        self.assertFalse(self.get("test_harness/permissions/user/action/kind/b", auth=USER_ROOT).json()["allowed"])


    def test_root_grant_permission_with_multipart_key(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind/a/b/c", auth=USER_ROOT).status_code)
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a/b/c", auth=USER_ROOT).json()["allowed"])
        self.assertFalse(self.get("test_harness/permissions/user/action/kind/a/b/d", auth=USER_ROOT).json()["allowed"])


    def test_root_grant_permission_with_multipart_key_chaining(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind/a/b", auth=USER_ROOT).status_code)
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a/b/c/d/e", auth=USER_ROOT).json()["allowed"])
        self.assertFalse(self.get("test_harness/permissions/user/action/kind/a/c/d/e", auth=USER_ROOT).json()["allowed"])


    def test_root_grant_permission_chaining(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind", auth=USER_ROOT).status_code)
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a/b/c", auth=USER_ROOT).json()["allowed"])


    def test_root_revoke_permission(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.delete("test_harness/permissions/user/action/kind", auth=USER_ROOT).status_code)
        self.assertFalse(self.get("test_harness/permissions/user/action/kind", auth=USER_ROOT).json()["allowed"])


    def test_root_revoke_parent_permission(self):
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.put("test_harness/permissions/user/action/kind/a/b/c", auth=USER_ROOT).status_code)
        self.assertEqual(200, self.delete("test_harness/permissions/user/action/kind", auth=USER_ROOT).status_code)
        self.assertFalse(self.get("test_harness/permissions/user/action/kind", auth=USER_ROOT).json()["allowed"])
        self.assertFalse(self.get("test_harness/permissions/user/action/kind/a", auth=USER_ROOT).json()["allowed"])
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a/b/c", auth=USER_ROOT).json()["allowed"])
        self.assertTrue(self.get("test_harness/permissions/user/action/kind/a/b/c/d", auth=USER_ROOT).json()["allowed"])



if __name__ == "__main__":
    unittest.main()

    
